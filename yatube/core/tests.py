from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    """Сервер возвращает код 404;
    при ошибке 404 используется кастомный шаблон."""
    def test_page_not_found(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
