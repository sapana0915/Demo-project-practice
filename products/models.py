from django.db import models
from atomicloops.models import AtomicModel


# Create your models here.
class Category(AtomicModel):
    category_name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Product(AtomicModel):
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products_category')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
