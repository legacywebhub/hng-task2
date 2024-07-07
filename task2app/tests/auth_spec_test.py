import pytest, json
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from task2app.utils import generateOrgID, generateUserID
from task2app.models import User, Organisation




# FIXTURES

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "password123"
    }



# TESTS

@pytest.mark.django_db
def test_register_user_success(api_client, user_data):
    url = reverse('register')
    response = api_client.post(url, data=user_data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['status'] == 'success'
    assert 'accessToken' in response.data['data']
    assert response.data['data']['user']['firstName'] == user_data['firstName']
    assert response.data['data']['user']['lastName'] == user_data['lastName']
    assert response.data['data']['user']['email'] == user_data['email']
    
    user = User.objects.get(email=user_data['email'])
    assert user.firstName == user_data['firstName']
    assert user.lastName == user_data['lastName']
    
    org = Organisation.objects.filter(users=user).first()
    assert org is not None
    assert org.name == f"{user.firstName}'s Organisation"


@pytest.mark.django_db
def test_register_user_missing_fields(api_client):
    url = reverse('register')
    
    missing_fields_data = {
        "firstName": "",
        "lastName": "",
        "email": "",
        "password": ""
    }
    
    response = api_client.post(url, data=missing_fields_data, format='json')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert 'errors' in response.data


@pytest.mark.django_db
def test_register_user_duplicate_email(api_client, user_data):
    url = reverse('register')
    api_client.post(url, data=user_data, format='json')
    
    response = api_client.post(url, data=user_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_login_user_success(api_client, user_data):
    # Register the user first
    url_register = reverse('register')
    api_client.post(url_register, data=user_data, format='json')

    # Log in the user
    url_login = reverse('login')
    login_data = {
        "email": user_data['email'],
        "password": user_data['password']
    }
    response = api_client.post(url_login, data=login_data, format='json')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'
    assert 'accessToken' in response.data['data']


@pytest.mark.django_db
def test_login_user_invalid_credentials(api_client):
    url = reverse('login')
    invalid_data = {
        "email": "invalid@example.com",
        "password": "invalidpassword"
    }
    response = api_client.post(url, data=invalid_data, format='json')
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['status'] == 'Bad request'
    assert response.data['message'] == 'Authentication failed'



@pytest.mark.django_db
def test_get_user_organisations(api_client, user_data):
    # Register the user first
    url_register = reverse('register')
    response = api_client.post(url_register, data=user_data, format='json')
    token = response.data['data']['accessToken']
    
    # Add Authorization header
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # Create another organisation for the user
    user = User.objects.get(email=user_data['email'])
    org = Organisation.objects.create(
        orgId="org2",
        name="Organisation 2"
    )
    org.users.add(user)
    
    # Get organisations
    url_orgs = reverse('organisations')
    response = api_client.get(url_orgs)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['status'] == 'success'



@pytest.mark.django_db
def test_protected_views_without_authentication(api_client):
    url = reverse('organisations')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data['detail'] == 'Authentication credentials were not provided.'



@pytest.mark.django_db
def test_organisation_access(api_client, user_data):
    # Register the user first
    url_register = reverse('register')
    response = api_client.post(url_register, data=user_data, format='json')
    token = response.data['data']['accessToken']
    
    # Add Authorization header
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

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
    response = api_client.get(url_org)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
