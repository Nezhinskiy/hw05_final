from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User
from posts.urls import (GROUP_LIST, INDEX, POST_CREATE, POST_DETAIL,
                        POST_EDITE, PROFILE)
from users.urls import LOGIN


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create_user(username='TestNoAuthor')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.user_author = User.objects.create_user(username='TestAuthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый текст',
            group=cls.group,
        )

    def tearDown(self) -> None:
        cache.clear()

    def test_posts_urls_exists_at_desired_location(self):
        """Страницы доступны любому пользователю"""
        slug = PostURLTests.group.slug
        username = PostURLTests.user_author.username
        post_id = PostURLTests.post.id
        url_names = [
            reverse(INDEX),
            reverse(GROUP_LIST, kwargs={'slug': slug}),
            reverse(PROFILE, kwargs={'username': username}),
            reverse(POST_DETAIL, kwargs={'post_id': post_id}),
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = PostURLTests.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Страница `{address}` работает неправильно, '
                                 f'проверьте этот адрес в *urls.py*')

    def test_posts_url_redirect_authorized_client(self):
        """Страницы редиректят неавторизованного пользователя"""
        post_id = PostURLTests.post.id
        url_names = [
            reverse(POST_EDITE, kwargs={'post_id': post_id}),
            reverse(POST_CREATE),
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = PostURLTests.guest_client.get(address, follow=True)
                self.assertRedirects(
                    response,
                    reverse(LOGIN) + "?next=" + address
                )

    def test_edit_url_redirect_authorized_client(self):
        """Страница edit редиректит авторизованного НЕ автора поста"""
        post_id = PostURLTests.post.id
        response = PostURLTests.authorized_client.get(
            reverse(POST_EDITE, kwargs={'post_id': post_id}),
            follow=True
        )
        self.assertRedirects(
            response, reverse(POST_DETAIL, kwargs={'post_id': post_id})
        )

    def test_edit_url_exists_at_desired_location_author(self):
        """Страница edit доступна автору поста"""
        post_id = PostURLTests.post.id
        response = PostURLTests.author_client.get(
            reverse(POST_EDITE, kwargs={'post_id': post_id})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         f'Страница `/posts/{post_id}/edit/` '
                         f'работает неправильно, проверьте '
                         f'этот адрес в *urls.py*')

    def test_create_url_exists_at_desired_location_authorized_client(self):
        """Страница create доступна авторизованному пользователю"""
        response = PostURLTests.author_client.get(reverse(POST_CREATE))
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница `/create/` работает неправильно, '
                         'проверьте этот адрес в *urls.py*')

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница unexisting_page
        выдаёт 404 любому пользователю"""
        response = PostURLTests.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'Страница `/unexisting_page/` работает неправильно, '
                         'проверьте get_object_or_404 в *views.py*')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        slug = PostURLTests.group.slug
        username = PostURLTests.user_author.username
        post_id = PostURLTests.post.id
        url_templates_names = (
            (reverse(INDEX), 'posts/index.html'),
            (reverse(GROUP_LIST, kwargs={'slug': slug}),
             'posts/group_list.html'),
            (reverse(PROFILE, kwargs={'username': username}),
             'posts/profile.html'),
            (reverse(POST_DETAIL, kwargs={'post_id': post_id}),
             'posts/post_detail.html'),
            (reverse(POST_CREATE), 'posts/create_post.html'),
            (reverse(POST_EDITE, kwargs={'post_id': post_id}),
             'posts/create_post.html'),
        )
        for address, template in url_templates_names:
            with self.subTest(address=address):
                response = PostURLTests.author_client.get(address)
                self.assertTemplateUsed(response, template)
