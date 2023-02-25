from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Account, Transaction, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number']

    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name


class UserSerializerWithToken(CustomUserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id',
                  'first_name',
                  'last_name',
                  'email',
                  'phone_number', 'token']

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        return str(token.access_token)


class AccountSerializer(serializers.ModelSerializer):
    transaction_count = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ['id', 'name', 'user', 'balance', 'transaction_count']

    def get_transaction_count(self, obj):
        print(obj)
        transactions = Transaction.objects.filter(account_id=obj.id).count()
        return transactions


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
