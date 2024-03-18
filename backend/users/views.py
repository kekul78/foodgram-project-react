from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet

from api.paginators import PagePagination
from api.serializers import SubscribeSerializer
from .models import MyUserModel, Subscribe
from .serializers import (CustomUserSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = MyUserModel.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PagePagination

    @action(methods=['get'], detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        token = Token.objects.get(key=request.auth)
        user = get_object_or_404(MyUserModel, id=token.user_id)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @staticmethod
    def get_subscribe_data(request, id):
        subscriber = request.user
        author = get_object_or_404(MyUserModel, id=id)
        subscribe_chek = Subscribe.objects.filter(subscriber=subscriber,
                                                  author=author)
        return subscriber, author, subscribe_chek

    @action(methods=['post'], detail=True,
            permission_classes=(IsAuthenticated,),
            url_path='subscribe', url_name='subscribe')
    def subscribe(self, request, id):
        subscriber, author, subscribe_chek = self.get_subscribe_data(request,
                                                                     id)
        if request.method == 'POST':
            if subscribe_chek.exists() or subscriber == author:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscribeSerializer(author,
                                             context={'request': request})
            Subscribe.objects.create(
                subscriber=subscriber, author=author
            ).save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        subscriber, author, subscribe_chek = self.get_subscribe_data(request,
                                                                     id)
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
