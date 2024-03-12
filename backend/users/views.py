from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from api.paginators import PagePagination
from api.serializers import SubscribeSerializer
from .models import MyUserModel, Subscribe
from .serializers import (
    UserSerializer,
    UserTokenSerializer,
    SetPasswordSerializer
)
from .permissions import IsAuthenticated


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUserModel.objects.all()
    serializer_class = UserSerializer
    pagination_class = PagePagination

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        token = Token.objects.get(key=request.auth)
        user = get_object_or_404(MyUserModel, id=token.user_id)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=False,
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        user = request.user
        serializer = SetPasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user.password = request.data['new_password']
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True,
            permission_classes=(IsAuthenticated,),
            url_path='subscribe', url_name='subscribe')
    def subscribe(self, request, **kwargs):
        subscriber = request.user
        author = get_object_or_404(MyUserModel, id=kwargs['pk'])
        subscribe_chek = Subscribe.objects.filter(subscriber=subscriber,
                                                  author=author)

        if request.method == 'POST':
            if subscribe_chek.exists() or subscriber == author:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(author,
                                             context={"request": request})
            Subscribe.objects.create(
                subscriber=subscriber, author=author
            ).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not subscribe_chek.exists() or subscriber == author:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(Subscribe,
                                             subscriber=subscriber,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'],
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path='subscriptions', url_name='subscriptions',)
    def subscriptions(self, request):
        queryset = MyUserModel.objects.filter(
            subscribe__subscriber=self.request.user
        )
        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = SubscribeSerializer(pages, many=True,
                                             context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response('Вы ни на кого не подписаны.',
                        status=status.HTTP_400_BAD_REQUEST)


class GetTokenView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        user = get_object_or_404(MyUserModel, email=email)
        try:
            token = Token.objects.get(user=user)
            token.delete()
            token = Token.objects.create(user=user)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        return Response({'auth_token': str(token)},
                        status=status.HTTP_200_OK)


class DeleteTokenView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        token = Token.objects.get(key=request.auth)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
