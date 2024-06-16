from django.urls import include, path
from rest_framework.routers import DefaultRouter
from articles.views import ArticleViewSet

router = DefaultRouter()
router.register("articles", ArticleViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("latest/", ArticleViewSet.as_view({"get": "latest"}), name="latest_article"),
]


app_name = "articles"
