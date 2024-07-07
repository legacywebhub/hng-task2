from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from task2app.utils import generateOrgID, generateUserID
from task2app.models import User, Organisation

class UserRegistrationTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password123"
        }

    def test_register_user_success(self):
        url = reverse('register')
        response = self.client.post(url, data=self.user_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('accessToken', response.json()['data'])
        self.assertEqual(response.json()['data']['user']['firstName'], self.user_data['firstName'])
        self.assertEqual(response.json()['data']['user']['lastName'], self.user_data['lastName'])
        self.assertEqual(response.json()['data']['user']['email'], self.user_data['email'])

        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.firstName, self.user_data['firstName'])
        self.assertEqual(user.lastName, self.user_data['lastName'])

        org = Organisation.objects.filter(users=user).first()
        self.assertIsNotNone(org)
        self.assertEqual(org.name, f"{user.firstName}'s Organisation")

    def test_register_user_missing_fields(self):
        url = reverse('register')
        missing_fields_data = {
            "firstName": "",
            "lastName": "",
            "email": "",
            "password": ""
        }
        response = self.client.post(url, data=missing_fields_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('errors', response.json())

    def test_register_user_duplicate_email(self):
        url = reverse('register')
        self.client.post(url, data=self.user_data, content_type='application/json')
        
        response = self.client.post(url, data=self.user_data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_user_success(self):
        # Register the user first
        url_register = reverse('register')
        self.client.post(url_register, data=self.user_data, content_type='application/json')

        # Log in the user
        url_login = reverse('login')
        login_data = {
            "email": self.user_data['email'],
            "password": self.user_data['password']
        }
        response = self.client.post(url_login, data=login_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('accessToken', response.json()['data'])

    def test_login_user_invalid_credentials(self):
        url = reverse('login')
        invalid_data = {
            "email": "invalid@example.com",
            "password": "invalidpassword"
        }
        response = self.client.post(url, data=invalid_data, content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], 'Bad request')
        self.assertEqual(response.json()['message'], 'Authentication failed')

    def test_get_user_organisations(self):
        # Register the user first
        url_register = reverse('register')
        response = self.client.post(url_register, data=self.user_data, content_type='application/json')
        token = response.json()['data']['accessToken']

        # Add Authorization header
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        # Create another organisation for the user
        user = User.objects.get(email=self.user_data['email'])
        org = Organisation.objects.create(
            orgId="org2",
            name="Organisation 2"
        )
        org.users.add(user)

        # Get organisations
        url_orgs = reverse('organisations')
        response = self.client.get(url_orgs)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'success')

    def test_protected_views_without_authentication(self):
        url = reverse('organisations')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')

    def test_organisation_access(self):
        # Register the user first
        url_register = reverse('register')
        response = self.client.post(url_register, data=self.user_data, content_type='application/json')
        token = response.json()['data']['accessToken']

        # Add Authorization header
        self.client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {token}'

        # Create another user and organisation
        user2 = User.objects.create(
            userId=generateUserID(),
            firstName="Jane",
            lastName="Doe",
            email="jane.doe@example.com",
            password=make_password("password123")
        )
        org = Organisation.objects.create(
            orgId=generateOrgID(),
            name=f"{user2.firstName} Organisation"
        )
        org.users.add(user2)

        # Try to access the other user's organisation
        url_org = reverse('organisation', kwargs={'orgId': org.id})
        response = self.client.get(url_org)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
