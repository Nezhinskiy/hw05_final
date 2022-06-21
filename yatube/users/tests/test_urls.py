from http import HTTPStatus

from django.test import Client, TestCase
from posts.models import User


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create_user(username='TestNoAuthor')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_users_urls_exists_at_desired_location(self):
        """Страницы доступны любому пользователю"""
        url_names = [
            '/auth/signup/',
            '/auth/logout/',
            '/auth/login/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = UserURLTests.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Страница `{address}` работает неправильно, '
                                 f'проверьте этот адрес в *urls.py*')

    def test_users_urls_redirect_authorized_client(self):
        """Страницы редиректят неавторизованного пользователя"""
        url_names = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = UserURLTests.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_users_urls_uses_correct_template_anon(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = UserURLTests.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_users_urls_exists_at_desired_location_authorized_client(self):
        """Страницы доступны авторизованному пользователю"""
        url_names = [
            '/auth/password_change/',
            '/auth/password_change/done/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = UserURLTests.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Страница `{address}` работает неправильно, '
                                 f'проверьте этот адрес в *urls.py*')

    def test_users_urls_uses_correct_template_authorized(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = UserURLTests.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница unexisting_page
        выдаёт 404 любому пользователю"""
        response = UserURLTests.guest_client.get('/auth/unexisting_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Страница `/auth/unexisting_page/` работает неправильно, '
            'проверьте get_object_or_404 в *views.py*'
        )
