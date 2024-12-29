"""
Tests for the user API.
We would have public (unauthenticated) and private (authenticated) tests.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')

# Helper function to create a user for testing purposes
def create_user(**params):
    """ Create and return and a user """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """ Test the public features of the user API"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """ Test creating a user is successful """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email']) # retrieves the object form the db for the specified email
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """ Test that error is returned if user with email exists """
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """ Test an error is returned if password is less than 5 characters """
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)


    def test_create_token_for_user(self):
        """ Test that a token is generated for a valid user """
        user_details = {
           'name': 'Test Name',
           'email': 'test@example.com',
           'password': 'testpass123',
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """ Test that token is not created if invalid credentials are given """
        create_user(email='test@example.com', password='goodpass')
        payload = {
           'email': 'test@example.com',
           'password': 'badpass',
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """ Test posting a blank password returns an error """
        payload= {'email':'test@example.com', 'password':''}
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """ Test that authentication is required for users """
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserApiTests(TestCase):
    """ Test API requests that require authentication. """

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user) #we force the authentication because we dont wanna to test the authentication side of things for this request=

    def test_retrieve_profile_success(self):
        """ Test retrieving profile for logged in user. """
        res = self.client.get(ME_URL) #will retrieve the details of the currently authenticated user

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,{
             'name': self.user.name,
             'email': self.user.email
        })

    def test_post_me_not_allowed(self):
        """ Test POST is not allowed for the me endpoint. """
        #we are not modifying anything with the me endpoint hence POST should not work
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
         """ Test updating the user profile for the authenticated user. """
         payload =  {'name':'Updated name', 'password': 'newpassword123'}
         res = self.client.patch(ME_URL, payload)

         #we refresh the db so that our user values are refreshed in the db
         self.user.refresh_from_db()
         self.assertEqual(self.user.name, payload['name'])
         self.assertTrue(self.user.check_password(payload['password']))
         self.assertEqual(res.status_code, status.HTTP_200_OK)












