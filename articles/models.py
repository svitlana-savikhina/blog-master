from django.db import models
from django.conf import settings


class Article(models.Model):
    title = models.CharField(max_length=250)
    content = models.TextField(default="")
    pub_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
