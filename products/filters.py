from .models import Product, Category
from atomicloops.filters import AtomicDateFilter, AtomicTimeFilter


class ProductFilter(AtomicDateFilter, AtomicTimeFilter):
    class Meta:
        model = Product
        fields = {
            'productName': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['gte', 'lte'],
            'createdAt': ['date__gte', 'date__lte'],
        }


class CategoryFilter(AtomicDateFilter, AtomicTimeFilter):
    class Meta:
        model = Category
        fields = {
            'categoryName': ['icontains'],
        }
