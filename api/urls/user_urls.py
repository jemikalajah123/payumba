from django.urls import path
from api.views import user_views as views

urlpatterns = [
    path('login', views.login_user, name='token_obtain_pair'),
    path('register', views.register_user, name='register'),

    path('profile', views.get_user_profile, name="users-profile"),
    path('', views.get_users, name="users"),
    path('<str:pk>', views.get_user_by_id, name='user'),

    path('update/<str:pk>', views.update_user, name='user-update'),

    path('delete/<str:pk>', views.delete_user, name='user-delete'),

]
