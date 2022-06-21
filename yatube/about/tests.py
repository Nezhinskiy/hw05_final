from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

    def test_about_urls_exists_at_desired_location(self):
        """Страницы доступны любому пользователю"""
        url_names = [
            '/about/author/',
            '/about/tech/',
        ]
        for address in url_names:
            with self.subTest(address=address):
                response = AboutURLTests.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK,
                                 f'Страница `{address}` работает неправильно, '
                                 f'проверьте этот адрес в *urls.py*')

    def test_about_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        url_templates_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = AboutURLTests.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Несуществующая страница unexisting_page
        выдаёт 404 любому пользователю"""
        response = AboutURLTests.guest_client.get('/about//unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND,
                         'Страница `/about/unexisting_page/` работает '
                         'неправильно, проверьте get_object_or_404 '
                         'в *views.py*')
