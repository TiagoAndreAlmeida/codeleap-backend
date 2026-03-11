from rest_framework import serializers
from .models import Post, Like, Comment

class CommentSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField()

    class Meta:
        model = Comment
        fields = ['id', 'username', 'content', 'is_owner', 'created_datetime', 'updated_datetime']
        read_only_fields = ['id', 'username', 'is_owner', 'created_datetime', 'updated_datetime']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False

class PostSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'username', 'is_owner', 'is_liked', 'likes_count', 
            'comments_count', 'created_datetime', 'updated_datetime', 'title', 'content'
        ]
        read_only_fields = [
            'id', 'username', 'is_owner', 'is_liked', 'likes_count', 
            'comments_count', 'created_datetime', 'updated_datetime'
        ]

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False
