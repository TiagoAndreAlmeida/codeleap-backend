from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'created_datetime', 'updated_datetime', 'deleted')
    list_filter = ('deleted', 'created_datetime', 'author')
    search_fields = ('author__username', 'author__first_name', 'title', 'content')
    readonly_fields = ('created_datetime', 'updated_datetime')

    def get_queryset(self, request):
        return Post.objects.all()
