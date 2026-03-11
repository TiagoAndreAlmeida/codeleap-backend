from rest_framework import viewsets, status, permissions, mixins
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import F
from .models import Post, Like, Comment
from .serializers import PostSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ['like', 'comments']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        return Post.objects.filter(deleted=False)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_destroy(self, instance):
        instance.deleted = True
        instance.save()

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        with transaction.atomic():
            like_qs = Like.objects.filter(user=user, post=post)
            if like_qs.exists():
                like_qs.delete()
                Post.objects.filter(pk=post.pk, likes_count__gt=0).update(likes_count=F('likes_count') - 1)
                liked = False
            else:
                Like.objects.create(user=user, post=post)
                Post.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
                liked = True
        post.refresh_from_db()
        return Response({"liked": liked, "likes_count": post.likes_count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        post = self.get_object()
        if request.method == 'POST':
            serializer = CommentSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save(author=request.user, post=post)
                    Post.objects.filter(pk=post.pk).update(comments_count=F('comments_count') + 1)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        comments = Comment.objects.filter(post=post, deleted=False)
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)

class CommentViewSet(mixins.UpdateModelMixin, 
                     mixins.DestroyModelMixin, 
                     viewsets.GenericViewSet):
    """
    ViewSet for editing and deleting specific comments.
    Creation and listing remain in PostViewSet to maintain context.
    """
    queryset = Comment.objects.filter(deleted=False)
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.deleted = True
            instance.save()
            Post.objects.filter(pk=instance.post.pk, comments_count__gt=0).update(
                comments_count=F('comments_count') - 1
            )
