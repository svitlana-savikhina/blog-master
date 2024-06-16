import asyncio

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from rest_framework.viewsets import GenericViewSet

from articles.models import Article
from articles.permissions import IsOwnerOrReadOnly
from articles.serializers import (
    ArticleSerializer,
    ArticlesListSerializer,
    ArticlesDetailSerializer,
)
from articles.telegram_bot import send_notification_to_telegram


class ArticlePagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 100


class ArticleViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Article.objects.all().order_by("-pub_date")
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = ArticlePagination

    def get_serializer_class(self):
        if self.action == "list":
            return ArticlesListSerializer
        elif self.action == "retrieve":
            return ArticlesDetailSerializer
        return ArticleSerializer

    def perform_create(self, serializer):
        instance = serializer.save(author=self.request.user)
        asyncio.run(send_notification_to_telegram(instance.title, instance.content))

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"error": "You do not have permission to edit this article."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {"error": "You do not have permission to delete this article."},
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["get"])
    def latest(self, request):
        latest_article = self.queryset.first()

        if latest_article:
            serializer = self.get_serializer(latest_article)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "No articles found"}, status=status.HTTP_404_NOT_FOUND
            )

    def get_permissions(self):
        if self.action == "latest":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        return super().get_permissions()
