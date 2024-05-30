from rest_framework import serializers

from articles.models import Article
from user.serializers import UserSerializer


class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = "__all__"
        read_only_fields = ["author"]


class ArticlesListSerializer(ArticleSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return (
            obj.author.profile.username
            if obj.author.profile.username
            else obj.author.username
        )

    class Meta:
        model = Article
        fields = ["id", "title", "content", "pub_date", "author"]


class ArticlesDetailSerializer(ArticleSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ["id", "title", "content", "pub_date", "author"]
