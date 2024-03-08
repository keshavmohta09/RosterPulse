"""
This file contains all the urls used for users module
"""

from django.urls import path

from users.apis import auth

urlpatterns = [
    path("login/", auth.UserLoginAPI.as_view(), name="user-login"),
    path("login/refresh/", auth.UserRefreshAPI.as_view(), name="user-login-refresh"),
    path("logout/", auth.UserLogoutAPI.as_view(), name="user_logout"),
]
