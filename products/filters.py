from .models import Product
from atomicloops.filters import AtomicDateFilter, AtomicFilterSet

class ProductFilter(AtomicFilterSet):
    class Meta:
        model = Product
        fields = {
            'product_name': ['icontains'],
            'price': ['gte', 'lte'],
            'stock': ['gte', 'lte'],
            'created_at': ['date__gte', 'date__lte'],
        }


class CategoryFilter(AtomicFilterSet):
    class Meta:
        model = Product.category.field.related_model
        fields = {
            'category_name': ['icontains'],
        }