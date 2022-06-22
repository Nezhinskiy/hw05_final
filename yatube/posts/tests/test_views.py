import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User
from posts.urls import (ADD_COMMENT, FOLLOW_INDEX, GROUP_LIST, INDEX,
                        POST_CREATE, POST_DETAIL, POST_EDITE, PROFILE,
                        PROFILE_FOLLOW, PROFILE_UNFOLLOW)
from posts.views import POSTS_ON_PAGE

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
AMOUNT_TEST_POSTS = 13


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TestNoAuthor')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.user_author = User.objects.create_user(username='TestAuthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)

        cls.new_user = User.objects.create_user(username='NewTestNoAuthor')
        cls.new_authorized_client = Client()
        cls.new_authorized_client.force_login(cls.new_user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.random_group = Group.objects.create(
            title='Случайная группа',
            slug='random-slug',
            description='Неверное описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='big.gif',
            content=small_gif,
            content_type='image/gif'
        )
        test_posts = (
            Post(
                author=cls.user_author,
                text=f'Тестовый текст №{count_test_post}',
                group=cls.group,
                image=uploaded,
            )
            for count_test_post in range(AMOUNT_TEST_POSTS)
        )
        Post.objects.bulk_create(test_posts)
        cls.post = Post.objects.all().first()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def tearDown(self) -> None:
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        slug = PostViewsTests.group.slug
        username = PostViewsTests.user.username
        post_id = PostViewsTests.post.id
        templates_pages_names = {
            reverse(INDEX):
            'posts/index.html',
            reverse(GROUP_LIST, kwargs={'slug': slug}):
            'posts/group_list.html',
            reverse(PROFILE, kwargs={'username': username}):
            'posts/profile.html',
            reverse(POST_DETAIL, kwargs={'post_id': post_id}):
            'posts/post_detail.html',
            reverse(POST_CREATE):
            'posts/create_post.html',
            reverse(POST_EDITE, kwargs={'post_id': post_id}):
            'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTests.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        """Проверка формы редактирования и создания поста."""
        post_id = PostViewsTests.post.id
        pages_names = {
            reverse(POST_CREATE),
            reverse(POST_EDITE, kwargs={'post_id': post_id})
        }
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = PostViewsTests.author_client.get(reverse_name)
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.fields.ChoiceField,
                }
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = response.context.get(
                            'form'
                        ).fields.get(value)
                        self.assertIsInstance(form_field, expected)

    def test_post_edit(self):
        """При редактировании открывается конкретный пост"""
        post_id = PostViewsTests.post.id
        response = PostViewsTests.author_client.get(
            reverse(
                POST_EDITE,
                kwargs={'post_id': post_id}
            )
        )
        self.assertEqual(response.context.get('form').instance.id, post_id)

    def test_post_detail(self):
        """Открывается конкретный пост"""
        post_id = PostViewsTests.post.id
        response = self.client.get(
            reverse(
                POST_DETAIL,
                kwargs={'post_id': post_id}
            )
        )
        self.assertEqual(response.context.get('post').id, post_id)

    def test_index_group_post(self):
        """При создании поста с указанием группы,
        он появляется на странице index и на странице
        выбраной группы"""
        group_test = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        Post.objects.create(
            author=PostViewsTests.user,
            text='Новый тестовый текст',
            group=group_test,
        )
        post_in_model = Post.objects.all().first()
        slug = post_in_model.group.slug
        pages_names = {
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': slug})
        }
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    response.context['page_obj'][0],
                    post_in_model,
                    f'На странице {reverse_name} '
                    'пост не найден'
                )

    def test_random_group_post(self):
        """Проверка, что пост не попал в группу,
        для которой не был предназначен"""
        post = PostViewsTests.post
        random_group = PostViewsTests.random_group
        slug = random_group.slug
        response = self.client.get(
            reverse(GROUP_LIST, kwargs={'slug': slug})
        )
        self.assertNotIn(
            post,
            response.context['page_obj'],
            'Пост попал в неверную группу'
        )

    def paginator_views_test(self):
        """Paginator работает исправно, на страницах:
         index, group_list, profile отображаются
         новые посты отфильтрованных правильным образом"""
        slug = PostViewsTests.group.slug
        username = PostViewsTests.user.username
        pages_names = {
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': slug}),
            reverse(PROFILE, kwargs={'username': username}),
        }
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_ON_PAGE,
                    f'На странице 1 шаблона {reverse_name} '
                    'паджинатор работает неверно'
                )
                response = self.client.get(reverse(INDEX) + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    AMOUNT_TEST_POSTS - POSTS_ON_PAGE,
                    f'На странице 2 шаблона {reverse_name} '
                    'паджинатор работает неверно'
                )

    def test_content_post(self):
        """Автор, текст, группа и картинка отображаются правильно
         на страницах: index, group_list, profile, post_detail"""
        group_test = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        ugly_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='ugly.gif',
            content=ugly_gif,
            content_type='image/gif'
        )
        Post.objects.create(
            author=PostViewsTests.user_author,
            text='Новый тестовый текст',
            group=group_test,
            image=uploaded,
        )
        post_in_model = Post.objects.all().first()
        slug = post_in_model.group.slug
        username = post_in_model.author.username
        post_id = post_in_model.id
        pages_names = [
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': slug}),
            reverse(PROFILE, kwargs={'username': username}),
            reverse(POST_DETAIL, kwargs={'post_id': post_id})
        ]
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                if reverse_name != pages_names[-1]:
                    post = response.context['page_obj'][0]
                else:
                    post = response.context['post']
                self.assertEqual(
                    post.author,
                    post_in_model.author,
                    f'На странице шаблона {reverse_name} '
                    'автор поста не найден'
                )
                self.assertEqual(
                    post.text,
                    post_in_model.text,
                    f'На странице шаблона {reverse_name} '
                    'текст пост не найден'
                )
                self.assertEqual(
                    post.group,
                    post_in_model.group,
                    f'На странице шаблона {reverse_name} '
                    'группа поста не найдена'
                )
                self.assertEqual(
                    post.image,
                    post_in_model.image,
                    f'На странице шаблона {reverse_name} '
                    'картинка поста не найдена'
                )

    def test_add_comment(self):
        """Не авторизованный пользователь не может
        оставлять комментарии"""
        comments_count = Comment.objects.filter(
            post=PostViewsTests.post
        ).count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.client.post(
            reverse(ADD_COMMENT, kwargs={'post_id': PostViewsTests.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Comment.objects.filter(post=PostViewsTests.post).count(),
            comments_count,
            'Количество комментариев изменилось'
        )

    def test_cash_index(self):
        """Кэш страницы index работает корректно"""
        Post.objects.all().delete()
        cache.clear()
        test_text = 'first post'
        Post.objects.create(
            author=PostViewsTests.user_author,
            text=test_text,
        )
        Post.objects.create(
            author=PostViewsTests.user_author,
            text='second text',
        )
        response = self.client.get(reverse(INDEX))
        posts_count = len(response.context['page_obj'])
        self.assertEqual(
            posts_count,
            Post.objects.all().count(),
            'На странице шаблона index '
            'пост не найден'
        )
        Post.objects.get(text='second text').delete()
        self.assertEqual(
            posts_count,
            Post.objects.all().count() + 1,
            'На странице шаблона index '
            'после удаления поста из базы'
            'пост не найден'
        )

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может
         подписываться на других пользователей"""
        user = PostViewsTests.user
        username_author = PostViewsTests.user_author.username
        count_follows_before = Follow.objects.filter(user=user).count()
        PostViewsTests.authorized_client.get(
            reverse(PROFILE_FOLLOW, kwargs={'username': username_author})
        )
        count_follows_after = Follow.objects.filter(user=user).count()
        self.assertEqual(
            count_follows_after,
            count_follows_before + 1,
            'Новая подписка не добавилась'
        )
        self.assertTrue(
            Follow.objects.filter(
                user=user, author=PostViewsTests.user_author
            ).exists(),
            'Подписка сформировалась неверно'
        )

    def test_authorized_user_can_follow(self):
        """Авторизованный пользователь может
         подписываться на других пользователей"""
        user = PostViewsTests.user
        username_author = PostViewsTests.user_author.username
        PostViewsTests.authorized_client.get(
            reverse(PROFILE_FOLLOW, kwargs={'username': username_author})
        )
        count_follows_before = Follow.objects.filter(user=user).count()
        PostViewsTests.authorized_client.get(
            reverse(PROFILE_UNFOLLOW, kwargs={'username': username_author})
        )
        count_follows_after = Follow.objects.filter(user=user).count()
        self.assertEqual(
            count_follows_after,
            count_follows_before - 1,
            'Подписка не удалилась'
        )
        self.assertFalse(
            Follow.objects.filter(
                user=user, author=PostViewsTests.user_author
            ).exists(),
            'Подписка удалилась неколлектно'
        )

    def test_new_post_displayed_to_followers(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех,
        кто не подписан"""
        username_author = PostViewsTests.user_author.username
        PostViewsTests.authorized_client.get(
            reverse(PROFILE_FOLLOW, kwargs={'username': username_author})
        )
        new_post_in_model = Post.objects.create(
            author=PostViewsTests.user_author,
            text='Новый тестовый текст'
        )
        response = PostViewsTests.authorized_client.get(reverse(FOLLOW_INDEX))
        new_post_in_page_follower = response.context['page_obj'][0]
        self.assertEqual(
            new_post_in_page_follower,
            new_post_in_model,
            'Новая запись не появилась в ленте того,'
            'кто на неё подписан'
        )
        new_response = PostViewsTests.new_authorized_client.get(
            reverse(FOLLOW_INDEX)
        )
        new_post_in_page_unfollower = new_response.context['page_obj']
        self.assertEqual(
            len(new_post_in_page_unfollower),
            0,
            'Новая запись появилась в ленте того,'
            'кто на неё не подписан'
        )
