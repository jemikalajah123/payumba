from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from api.serializers import UserSerializerWithToken, CustomUserSerializer
from api.models import CustomUser
from rest_framework import status
from rest_framework.response import Response


@api_view(['POST'])
def login_user(request):
    data = request.data
    email = data['email']
    password = data['password']

    # Authenticate the user using the CustomUser model
    user = authenticate(request, username=email, password=password)

    # If the user is authenticated, generate an auth token and return it in the response
    if user:
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)
    # If the user is not authenticated, return a 401 Unauthorized response
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def register_user(request):
    data = request.data
    if CustomUser.objects.filter(email=data['email']).exists():
        return Response({'error': 'Email address already exists'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data['password'])
            user.save()
            serializer = UserSerializerWithToken(user, many=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except AssertionError as error:
        message = {'detail': error}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    serializer = CustomUserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    users = CustomUser.objects.all()
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_by_id(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)
    except CustomUser.DoesNotExist:
        return Response({'message': "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = CustomUserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = CustomUserSerializer(user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request, pk):
    try:
        user = CustomUser.objects.get(id=pk)
    except CustomUser.DoesNotExist:
        return Response({'error': "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    user.delete()
    return Response({'message': 'User was deleted'}, status=status.HTTP_200_OK)
