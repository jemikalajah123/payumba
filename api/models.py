# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, PermissionsMixin


class BaseModel(models.Model):
    objects = models.Manager()

    class Meta:
        abstract = True


class CustomUser(AbstractUser, PermissionsMixin):
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    # Set related_name for user_permissions to avoid clash with auth.User model
    user_permissions = models.ManyToManyField(
        to='auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='The permissions this user has'
    )

    # Set related_name for groups to avoid clash with auth.User model
    groups = models.ManyToManyField(
        to=Group,
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to'
    )


class Account(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    balance = models.FloatField(null=True, blank=True, default=0.0)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Transaction(BaseModel):
    credit = 'credit'
    debit = 'debit'

    STATE = (
        (credit, credit),
        (debit, debit)
    )
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    amount = models.FloatField(null=True, blank=True, default=0.0)
    transaction_type = models.CharField(max_length=10, choices=STATE, default=credit)
    description = models.TextField(null=True, blank=True)
    user_ip = models.CharField(max_length=200, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.created_at)
