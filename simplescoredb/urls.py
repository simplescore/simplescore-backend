"""simplescoredb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from simplescoredb.db import views

router = routers.DefaultRouter()
router.register(r'song', views.SongViewSet)
router.register(r'chart', views.ChartViewSet)
router.register(r'score', views.ScoreViewSet)
router.register(r'user', views.UserViewSet)

urlpatterns = [
    path('score/api/v0/', include(router.urls)),
    path('score/api/v0/auth/register', views.RegisterView.as_view()),
    path('score/api/v0/auth/login', TokenObtainPairView.as_view()),
    path('score/api/v0/auth/refresh', TokenRefreshView.as_view()),
    path('score/api/v0/api-auth', include('rest_framework.urls', namespace='rest_framework'))
]
