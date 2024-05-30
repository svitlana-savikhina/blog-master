from django.urls import include, path
from rest_framework.routers import DefaultRouter
from articles.views import ArticleViewSet

router = DefaultRouter()
router.register("articles", ArticleViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "articles"
