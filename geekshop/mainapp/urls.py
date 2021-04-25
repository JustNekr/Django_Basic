from django.urls import path
from .views import main, products, contact

urlpatterns = [
    path('', main),
    path('products/', products),
    path('contact/', contact),
]
