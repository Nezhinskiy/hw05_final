import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import CommentForm, PostForm
from posts.models import Comment, Group, Post, User
from posts.urls import (ADD_COMMENT, POST_CREATE, POST_DETAIL, POST_EDITE,
                        PROFILE)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TesterNoAuthor')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.user_author = User.objects.create_user(username='TesterAuthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_edit = Group.objects.create(
            title='Вторая тестовая группа',
            slug='double-test-slug',
            description='Второе тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый текст',
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Отправленная валидная форма со стрпницы
        post_create создает запись в Post и редиректит
        на страницу profile."""
        posts_count = Post.objects.count()
        group = PostCreateFormTests.group
        big_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'      
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='big.gif',
            content=big_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый тестовый текст',
            'group': group.pk,
            'image': uploaded
        }
        response = PostCreateFormTests.author_client.post(
            reverse(POST_CREATE),
            data=form_data,
            follow=True
        )
        username = PostCreateFormTests.user_author.username
        self.assertRedirects(
            response, reverse(PROFILE, kwargs={'username': username})
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count + 1,
            'Новых постов не создалось'
        )
        new_post = Post.objects.all().order_by('id').last()
        self.assertEqual(
            new_post.author,
            PostCreateFormTests.user_author,
            'Поле "author" не создалось'
        )
        self.assertEqual(
            new_post.text,
            form_data['text'],
            'Поле "text" не создалось'
        )
        self.assertEqual(
            new_post.group.pk,
            form_data['group'],
            'Поле "group" не создалось'
        )
        self.assertEqual(
            new_post.image,
            'posts/big.gif',
            'Поле "image" не создалось'
        )

    def test_edit_post(self):
        """Отредактированная валидная форма со станицы
        post_edit редактирует существующую запись в Post
        и редиректит на страницу post_detail."""
        posts_count = Post.objects.count()
        group = PostCreateFormTests.group_edit
        medium_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='medium.gif',
            content=medium_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Отредактированный тестовый текст',
            'group': group.pk,
            'image': uploaded
        }
        post_id = PostCreateFormTests.post.id
        response = PostCreateFormTests.author_client.post(
            reverse(POST_EDITE, kwargs={'post_id': post_id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(POST_DETAIL, kwargs={'post_id': post_id})
        )
        self.assertEqual(
            Post.objects.count(),
            posts_count,
            'Количество постов изменилось'
        )
        edited_post = Post.objects.get(id=post_id)
        self.assertEqual(
            edited_post.author,
            PostCreateFormTests.user_author,
            'Поле "author" не отредактировалось'
        )
        self.assertEqual(
            edited_post.text,
            form_data['text'],
            'Поле "text" не отредактировалось'
        )
        self.assertEqual(
            edited_post.group.pk,
            form_data['group'],
            'Поле "group" не отредактировалось'
        )
        self.assertEqual(
            edited_post.image,
            'posts/medium.gif',
            'Поле "image" не отредактировалось'
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='TesterNoAuthor')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)

        cls.user_author = User.objects.create_user(username='TesterAuthor')
        cls.author_client = Client()
        cls.author_client.force_login(cls.user_author)

        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый текст'
        )

        cls.form = CommentForm()

    def test_create_comment(self):
        """После успешной отправки CommentForm авторизованным
         пользователем, происходит редирект на страницу поста и
         там появляется новый комментарий"""
        post = CommentFormTests.post
        comments_count = Comment.objects.filter(post=post).count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = CommentFormTests.user_client.post(
            reverse(ADD_COMMENT, kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse(POST_DETAIL, kwargs={'post_id': post.id})
        )
        self.assertEqual(
            Comment.objects.filter(post=post).count(),
            comments_count + 1,
            'Количество комментариев не изменилось'
        )
        new_comment = response.context['comments'][0]
        self.assertEqual(
            new_comment.text,
            form_data['text'],
            'Поле "text" не создалось'
        )
