from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Invertemos a ordem: API primeiro, Admin depois
    path('api/v1/', include('posts.urls')),
    path('', admin.site.urls),
]
