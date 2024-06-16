from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from articles.models import Article


class ArticleViewSetTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@test.com", password="testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.article = Article.objects.create(
            title="Test Title", content="Test Content", author=self.user
        )

    def test_create_article(self):
        url = reverse("articles:article-list")
        data = {"title": "New Title", "content": "New Content"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.get(id=response.data["id"]).title, "New Title")

    def test_get_article(self):
        url = reverse("articles:article-detail", args=[self.article.id])
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.article.title)

    def test_update_article(self):
        url = reverse("articles:article-detail", args=[self.article.id])
        data = {"title": "Updated Title", "content": "Updated Content"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, "Updated Title")

    def test_delete_article(self):
        url = reverse("articles:article-detail", args=[self.article.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 0)
