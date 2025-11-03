from django.shortcuts import render
from rest_framework import viewsets
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from atomicloops.viewsets import AtomicViewSet
from .filters import ProductFilter, CategoryFilter
# Create your views here.


class ProductViewSet(AtomicViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    search_fields = ['product_name']
    ordering_fields = ['price', 'stock', 'created_at', 'updated_at']
    ordering = ['-created_at']


class CategoryViewSet(AtomicViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
