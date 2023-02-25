from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from api.serializers import AccountSerializer
from api.models import Account, Transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response

contents_per_page = 10


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_accounts(request):
    query = request.query_params.get('keyword')
    if query is None:
        query = ''
    accounts = Account.objects.filter(
        name__icontains=query).order_by('-created_at')
    page = request.query_params.get('page')
    paginator = Paginator(accounts, contents_per_page)

    try:
        accounts = paginator.page(page)
    except PageNotAnInteger:
        accounts = paginator.page(1)
    except EmptyPage:
        accounts = paginator.page(paginator.num_pages)

    if page is None:
        page = 1

    page = int(page)
    print('Page:', page)
    serializer = AccountSerializer(accounts, many=True)
    return Response({'accounts': serializer.data, 'page': page, 'pages': paginator.num_pages})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account(request, pk):
    try:
        account = Account.objects.get(id=pk)
    except Account.DoesNotExist:
        return Response({'error': "Account does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = AccountSerializer(account, many=False)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_account(request):
    user = request.user
    data = request.data
    account = Account.objects.create(
        user=user,
        name=data['name']
    )
    serializer = AccountSerializer(account, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_account(request, pk):
    try:
        account = Account.objects.get(id=pk)
    except Account.DoesNotExist:
        return Response({'error': "Account does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    serializer = AccountSerializer(account, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request, pk):
    try:
        account = Account.objects.get(id=pk)
    except Account.DoesNotExist:
        return Response({'error': "Account does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    account.delete()
    return Response({'message': 'Account was deleted'}, status=status.HTTP_200_OK)
