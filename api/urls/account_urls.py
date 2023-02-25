from django.urls import path
from api.views import account_view as views
from api.views import transaction_view as trnx_views

urlpatterns = [
    path('', views.get_accounts, name="accounts"),

    path('add', views.create_account, name="account-create"),

    path('<str:pk>', views.get_account, name="account"),
    path('<str:pk>/transactions', trnx_views.list_transactions, name="transactions"),
    path('<str:pk>/transaction', trnx_views.create_transactions, name="create_transactions"),
    path('update/<str:pk>', views.update_account, name="account-update"),
    path('delete/<str:pk>', views.delete_account, name="account-delete"),
]