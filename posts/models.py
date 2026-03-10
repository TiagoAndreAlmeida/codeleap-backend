from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_datetime']

    def __str__(self):
        return self.title

    @property
    def username(self):
        return self.author.first_name if self.author.first_name else self.author.username
