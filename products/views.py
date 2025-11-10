from atomicloops.viewsets import AtomicViewSet
from .filters import ProductFilter, CategoryFilter
from .models import Product, Category, ProductVideoImage
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ProductImageVideoSerializer,
)


class CategoryViewSet(AtomicViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filterset_class = CategoryFilter
    permission_classes = ()


class ProductViewSet(AtomicViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = ()
    filterset_class = ProductFilter
    search_fields = ['productName']
    ordering_fields = ['price', 'stock']
    ordering = ('-createdAt',)


class ImageVideoViewSet(AtomicViewSet):
    queryset = ProductVideoImage.objects.all()
    serializer_class = ProductImageVideoSerializer
    permission_classes = ()
