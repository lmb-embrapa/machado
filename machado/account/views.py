from rest_framework.response import Response
from rest_framework import viewsets, status
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import NotFound

#Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import UserSerializer
import re

class PublicUserActions(viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="User Login",
        operation_description="Authenticate a user and return an authentication token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
            },
            required=['email', 'password']
        ),
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={"application/json": {"token": "your_auth_token"}}
            ),
            400: openapi.Response(
                description="Bad Request - Email and password are required",
                examples={"application/json": "Email and password are required"}
            ),
            401: openapi.Response(
                description="Unauthorized - User not exists or password is incorrect",
                examples={"application/json": "User not exists or password is incorrect"}
            ),
        }
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if (email == None or password == None):
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Email and password are required")
        
        try:
            userRequest = User.objects.get(email=email)
            user = authenticate(request, username=userRequest.username, password=password)
            if user:
                token, created = Token.objects.get_or_create(user=user)
                serializer = UserSerializer(user, many=False)
                return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            pass
        
        return Response(status=status.HTTP_401_UNAUTHORIZED, data="User not exists or password is incorrect")

class AuthenticatedUserActions(viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="User Logout",
        operation_description="Invalidate the user's authentication token to log them out.",
        responses={
            200: openapi.Response(description="Logout successful"),
            400: openapi.Response(description="Token not exists")
        }
    )
    @action(detail=False, methods=['post'])
    def logout(self, request):
        token = request.auth
        if token:
            token.delete()
            return Response(status=status.HTTP_200_OK, data="Logout success")
        return Response(status=status.HTTP_400_BAD_REQUEST, data="Token not exists")

class AdminUserActions(viewsets.GenericViewSet):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_summary="List all users",
        operation_description="Retrieve a list of all users in the system.",
        responses={
            200: openapi.Response(
                description="A list of all users",
                schema=UserSerializer(many=True)
            ),
            404: openapi.Response(
                description="No users found",
                examples={"application/json": {"msg": "No users found."}}
            ),
        }
    )
    @action(detail=False, methods=['get'])
    def list(self, request):
        users = User.objects.all()
        if not users.exists():
            return Response({"msg": "No users found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_summary="Retrieve user by ID",
        operation_description="Fetch details of a user by providing their unique ID.",
        manual_parameters=[
            openapi.Parameter(
                'id', 
                openapi.IN_QUERY, 
                description="Unique ID of the user", 
                type=openapi.TYPE_INTEGER, 
                required=True
            )
        ],
        responses={
            200: UserSerializer(),
            404: 'User not found'
        }
    )
    @action(detail=False, methods=['get'])
    def listUserById(self, request, id=None):
        user = User.objects.filter(pk=id).first()
        if not user:
            return Response({"msg": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Retrieve user by username",
        operation_description="Fetch details of a user by providing their unique username.",
        manual_parameters=[
            openapi.Parameter(
                'username',
                openapi.IN_QUERY,
                description="Unique username of the user",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: UserSerializer(),
            404: openapi.Response(description="User not found")
        }
    )
    @action(detail=False, methods=['get'])
    def listUserByUsername(self, request, username=None):

        try:
            user = User.objects.filter(username__icontains=username)
        except User.DoesNotExist:
            raise NotFound({"msg": "User not found."})
        
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Create a new user",
        operation_description="Create a new user with the specified username, email, password, and optional fields like first name, last name, and admin status.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username (required)'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password (required)'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name (optional)'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name (optional)'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address (required)'),
                'is_staff': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Admin status, 1 for True, 0 for False (optional)',
                    enum=[0, 1]
                )
            },
            required=['username', 'email', 'password']
        ),
        responses={
            201: openapi.Response(description="User created"),
            400: openapi.Response(description="User not created - Username and password are required")
        }
    )
    @action(detail=False, methods=['post'])
    def create(self, request):
        requestUsername = request.data.get('username')
        requestPassword = request.data.get('password')
        requestEmail = request.data.get('email')
        requestFirstName = request.data.get('first_name', '')
        requestLastName = request.data.get('last_name', '')
        requestIsStaff = request.data.get('is_staff')
        if requestUsername == None or requestPassword == None or requestEmail == None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Username, email and password are required")

        if len(requestUsername) < 3 or len(requestPassword) < 3:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Username and password must be at least 3 characters long")

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, requestEmail):
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid email format")
    
        if requestIsStaff == 1:
            requestIsStaff = True
        else:
            requestIsStaff = False

        user = User.objects.create_user(
            username=requestUsername, password=requestPassword, first_name=requestFirstName, 
            last_name=requestLastName, email=requestEmail, is_staff=requestIsStaff
        )
        if user:
            return Response(status=status.HTTP_201_CREATED, data="User created")
        return Response(status=status.HTTP_400_BAD_REQUEST, data="User not created")

    @swagger_auto_schema(
        operation_summary="Delete a user",
        operation_description="Delete a user by their ID.",
        responses={
            200: openapi.Response(description="User deleted"),
            404: openapi.Response(description="User not found")
        }
    )
    @action(detail=False, methods=['delete'])
    def delete(self, request, id=None):
        user = User.objects.filter(pk=id).first()
        if user:
            user.delete()
            return Response(status=status.HTTP_200_OK, data="User deleted")
        return Response(status=status.HTTP_404_NOT_FOUND, data="User not found")

    @swagger_auto_schema(
        operation_summary="Update user information",
        operation_description="Update an existing user's details, where is_staff should be 1 (True) or 0 (False).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
                'is_staff': openapi.Schema(
                    type=openapi.TYPE_INTEGER, 
                    description='Admin status, 1 for True, 0 for False',
                    enum=[0, 1]
                )
            }
        ),
        responses={
            200: openapi.Response(description="User updated"),
            404: openapi.Response(description="User not found")
        }
    )
    @action(detail=False, methods=['put'])
    def update(self, request, id=None):
        user = User.objects.filter(pk=id).first()
        if user:
            username = request.data.get('username')
            firstName = request.data.get('first_name')
            lastName = request.data.get('last_name')
            email = request.data.get('email')
            password = request.data.get('password')
            isStaff = request.data.get('is_staff')
            if username:
                user.username = username
            if firstName:
                user.first_name = firstName
            if lastName:
                user.last_name = lastName
            if email:
                user.email = email
            if password:
                user.set_password(password)
            if isStaff:
                if isStaff == 1:
                    user.is_staff = True
                elif isStaff == 0:
                    user.is_staff = False
            user.save()
            return Response(status=status.HTTP_200_OK, data="User updated")
        return Response(status=status.HTTP_404_NOT_FOUND, data="User not found")