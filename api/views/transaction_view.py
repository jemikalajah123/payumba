import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from api.serializers import TransactionSerializer
from api.models import Account, Transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response

contents_per_page = 10


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_transactions(request, pk):
    try:
        account = Account.objects.get(id=pk)
    except Account.DoesNotExist:
        return Response({'error': "Account does not exist"}, status=status.HTTP_400_BAD_REQUEST)

    query = request.query_params.get('keyword')
    if query is None:
        query = ''
    transactions = Transaction.objects.filter(
        description__icontains=query, account=account.id).order_by('-created_at')
    page = request.query_params.get('page')
    paginator = Paginator(transactions, contents_per_page)

    try:
        transactions = paginator.page(page)
    except PageNotAnInteger:
        transactions = paginator.page(1)
    except EmptyPage:
        transactions = paginator.page(paginator.num_pages)

    if page is None:
        page = 1

    page = int(page)
    print('Page:', page)
    serializer = TransactionSerializer(transactions, many=True)
    return Response({'transactions': serializer.data, 'page': page, 'pages': paginator.num_pages})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transactions(request, pk):
    try:
        account = Account.objects.get(id=pk)
    except Account.DoesNotExist:
        return Response({'error': "Account does not exist"}, status=status.HTTP_400_BAD_REQUEST)
    data = request.data
    amount = float(data['amount'])
    transaction_type = data['type']
    description = data['description']

    if transaction_type not in ('credit', 'debit'):
        return Response({'error': 'Invalid transaction type'}, status=status.HTTP_400_BAD_REQUEST)

    if not amount or not transaction_type:
        return Response({'error': 'Invalid transaction amount'}, status=status.HTTP_400_BAD_REQUEST)

    if transaction_type == 'debit' and account.balance < amount:
        return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

    user_ip = requests.get('https://api.ipify.org').text

    # Create the transaction
    transaction = Transaction.objects.create(
        account=account,
        amount=amount,
        transaction_type=transaction_type,
        description=description,
        user_ip=user_ip
    )
    account.balance += amount if transaction_type == 'credit' else -amount
    account.save()
    serializer = TransactionSerializer(transaction, many=False)
    return Response(serializer.data)
