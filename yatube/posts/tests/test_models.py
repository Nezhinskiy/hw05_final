from django.test import TestCase
from posts.models import DISPLAYED_LETTERS, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост',
        )

    def test_models_post_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        text = post.text
        self.assertEqual(
            str(post),
            text[:DISPLAYED_LETTERS],
            '__str__ модели Post работает некорректно'
        )

    def test_models_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        title = group.title
        self.assertEqual(
            str(group), title, '__str__ модели Group работает некорректно'
        )
