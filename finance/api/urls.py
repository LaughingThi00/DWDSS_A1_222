from django.urls import path, include
from .views import StockView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('stock/', StockView.as_view()),
]