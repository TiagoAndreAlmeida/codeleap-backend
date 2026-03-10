from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'username', 'is_owner', 'created_datetime', 'updated_datetime', 'title', 'content']
        read_only_fields = ['id', 'username', 'is_owner', 'created_datetime', 'updated_datetime']

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False
