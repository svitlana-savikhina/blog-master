from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class UserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@test.com", password="password")
        self.profile = self.user.profile
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com", password="password"
        )

    def test_register_user(self):
        url = reverse("user:create")
        data = {"email": "newuser@test.com", "password": "newpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)  # 2 in setUp + 1 new user
        self.assertEqual(
            User.objects.get(email="newuser@test.com").email, "newuser@test.com"
        )

    def test_obtain_token(self):
        url = reverse("user:token_obtain_pair")
        data = {"email": "user@test.com", "password": "password"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token(self):
        obtain_url = reverse("user:token_obtain_pair")
        refresh_url = reverse("user:token_refresh")

        obtain_data = {"email": "user@test.com", "password": "password"}
        obtain_response = self.client.post(obtain_url, obtain_data, format="json")

        refresh_data = {"refresh": obtain_response.data["refresh"]}
        refresh_response = self.client.post(refresh_url, refresh_data, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_get_profile(self):
        self.client.force_authenticate(self.user)
        url = reverse("user:profile")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_profile(self):
        self.client.force_authenticate(self.user)
        url = reverse("user:profile")
        data = {"email": "updateduser@test.com", "username": "newname"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updateduser@test.com")
        self.assertEqual(self.user.profile.username, "newname")

    def test_get_user_details(self):
        self.client.force_authenticate(self.user)
        url = reverse("user:manage")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)

    def test_update_user_details(self):
        self.client.force_authenticate(self.user)
        url = reverse("user:manage")
        data = {"email": "updateduser@test.com", "password": "newpassword"}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "updateduser@test.com")
        self.assertTrue(self.user.check_password("newpassword"))
