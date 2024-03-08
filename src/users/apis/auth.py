"""
This file contains all the APIs related to user authentication
"""

from django.contrib.auth import authenticate
from django.db import IntegrityError
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import BlacklistedToken, OutstandingToken

from users.constants import TOKEN_IS_ALREADY_BLACK_LISTED, USER_LOGGED_OUT_SUCCESSFULLY
from utils.constants import INVALID_FIELD_VALUE
from utils.response import CustomResponse


class UserLoginAPI(APIView):
    """
    This API is used for login the user
    Response codes: 200, 400
    """

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    def post(self, request, *args, **kwargs):

        serializer = self.InputSerializer(data=request.data)
        if not serializer.is_valid():
            return CustomResponse(errors=serializer.errors, status=HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        user = authenticate(
            email=validated_data["email"], password=validated_data["password"]
        )
        if not user:
            return CustomResponse(
                errors="No active account found with the given credentials",
                status=HTTP_400_BAD_REQUEST,
            )

        token = TokenObtainPairSerializer.get_token(user=user)

        response = CustomResponse(
            data={"access_token": str(token.access_token)}, status=HTTP_200_OK
        )
        response.set_cookie(key="refresh_token", value=str(token), httponly=True)
        return response


class UserRefreshAPI(APIView):
    """
    This API used to refresh token
    Cookies: refresh_token
    Response codes: 200, 400, 401
    """

    def get(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        serializer = TokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            if not serializer.is_valid():
                return CustomResponse(
                    errors=serializer.errors, status=HTTP_400_BAD_REQUEST
                )
        except TokenError as error:
            return CustomResponse(errors=str(error), status=HTTP_400_BAD_REQUEST)

        return CustomResponse(
            data={"access_token": serializer.validated_data["access"]},
            status=HTTP_200_OK,
        )


class UserLogoutAPI(APIView):
    """
    This API used to logout the user
    Cookies: refresh_token
    Response codes: 200, 400
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        try:
            outstanding_token = OutstandingToken.objects.get(
                token=refresh_token, expires_at__gt=now()
            )
        except OutstandingToken.DoesNotExist:
            return CustomResponse(
                errors=INVALID_FIELD_VALUE.format(field="refresh_token")
            )

        try:
            # Marking refresh token as blacklisted token
            BlacklistedToken.objects.create(token=outstanding_token)
        except IntegrityError:
            return CustomResponse(
                errors=TOKEN_IS_ALREADY_BLACK_LISTED, status=HTTP_400_BAD_REQUEST
            )

        return CustomResponse(data=USER_LOGGED_OUT_SUCCESSFULLY, status=HTTP_200_OK)
