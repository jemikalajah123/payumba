from api.serializers import TransactionSerializer
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Account, Transaction


class CreateTransactionsAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.account = Account.objects.create(owner=self.user, balance=1000)

    def test_create_credit_transaction(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('create_transactions', kwargs={'pk': self.account.id})
        data = {
            'amount': '500.00',
            'type': 'credit',
            'description': 'Test credit transaction'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Account.objects.get(id=self.account.id).balance, 1500.00)

    def test_create_debit_transaction(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('create_transactions', kwargs={'pk': self.account.id})
        data = {
            'amount': '200.00',
            'type': 'debit',
            'description': 'Test debit transaction'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Transaction.objects.count(), 1)
        self.assertEqual(Account.objects.get(id=self.account.id).balance, 800.00)

    def test_create_invalid_transaction_type(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('create_transactions', kwargs={'pk': self.account.id})
        data = {
            'amount': '500.00',
            'type': 'invalid',
            'description': 'Test invalid transaction'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(Account.objects.get(id=self.account.id).balance, 1000.00)

    def test_create_insufficient_balance(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('create_transactions', kwargs={'pk': self.account.id})
        data = {
            'amount': '1500.00',
            'type': 'debit',
            'description': 'Test insufficient balance'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Transaction.objects.count(), 0)
        self.assertEqual(Account.objects.get(id=self.account.id).balance, 1000.00)

class ListTransactionsTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.account = Account.objects.create(name='testaccount')
        self.transactions = [
            Transaction.objects.create(
                description='test transaction 1', account=self.account),
            Transaction.objects.create(
                description='test transaction 2', account=self.account)
        ]

    def tearDown(self):
        self.user.delete()
        self.token.delete()
        self.account.delete()
        Transaction.objects.all().delete()

    def test_list_transactions_with_authentication(self):
        """
        Test that authenticated user can list transactions.
        """
        url = reverse('list_transactions', args=[self.account.pk])
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'transactions': TransactionSerializer(
                self.transactions, many=True).data,
            'page': 1,
            'pages': 1
        }
        self.assertEqual(response.data, expected_data)

    def test_list_transactions_without_authentication(self):
        """
        Test that unauthenticated user cannot list transactions.
        """
        url = reverse('list_transactions', args=[self.account.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AccountTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', email='testuser@test.com', password='testpass'
        )
        self.client.force_authenticate(user=self.user)

        self.account = Account.objects.create(user=self.user, name='Test Account')

    def test_get_accounts(self):
        url = reverse('get-accounts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['accounts']), 1)

    def test_get_account(self):
        url = reverse('get-account', args=[self.account.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Account')

    def test_create_account(self):
        url = reverse('create-account')
        data = {'name': 'New Account'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Account')

    def test_update_account(self):
        url = reverse('update-account', args=[self.account.id])
        data = {'name': 'Updated Account'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Account')

    def test_delete_account(self):
        url = reverse('delete-account', args=[self.account.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Account was deleted')



User = get_user_model()

class UserTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='testuser@test.com', password='testpassword')
        self.client = APIClient()

    def test_login_user(self):
        url = '/api/users/login/'
        data = {'email': 'testuser@test.com', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_register_user(self):
        url = '/api/users/register/'
        data = {'email': 'newuser@test.com', 'password': 'newpassword', 'first_name': 'New', 'last_name': 'User'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_get_user_profile(self):
        url = '/api/users/profile/'
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@test.com')

    def test_get_users(self):
        url = '/api/users/'
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_user_by_id(self):
        new_user = User.objects.create_user(email='newuser@test.com', password='newpassword')
        url = f'/api/users/{new_user.id}/'
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newuser@test.com')

    def test_update_user(self):
        url = f'/api/users/update/{self.user.id}/'
        data = {'first_name': 'Updated', 'last_name': 'User'}
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')

    def test_delete_user(self):
        new_user = User.objects.create_user(email='newuser@test.com', password='newpassword')
        url = f'/api/users/delete/{new_user.id}/'
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'User was deleted')
