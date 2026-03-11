from django.contrib import admin
from .models import Post, Like

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'likes_count', 'created_datetime', 'updated_datetime', 'deleted')
    list_filter = ('deleted', 'created_datetime', 'author')
    search_fields = ('author__username', 'author__first_name', 'title', 'content')
    readonly_fields = ('created_datetime', 'updated_datetime', 'likes_count')

    def get_queryset(self, request):
        return Post.objects.all()

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at', 'user', 'post')
    search_fields = ('user__username', 'user__first_name', 'post__title')
    readonly_fields = ('created_at',)
