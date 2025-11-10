from rest_framework import serializers

from atomicloops.serializers import AtomicSerializer

from .models import Product, Category, ProductVideoImage


class CategorySerializer(AtomicSerializer):
    class Meta:
        model = Category
        fields = ("id",
                  "categoryName",
                  "description",
                  "createdAt",
                  "updatedAt")
        get_fields = fields
        list_fields = fields


class ProductSerializer(AtomicSerializer):
    categoryName = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='categoryName',
        source='category'
    )

    class Meta:
        model = Product
        fields = (
            "id",
            "productName",
            "description",
            "price",
            "stock",
            "categoryName",
            "totalStockPrice",
            "createdAt",
            "updatedAt"
        )
        get_fields = fields
        list_fields = fields

    def validate_price(self, value):
        if value < 0:
            message = "Price must be a positive value."
            raise serializers.ValidationError(message)
        return value

    def validate_stock(self, value):
        if value < 0:
            message = "Stock must be a non-negative integer."
            raise serializers.ValidationError(message)
        return value

    def create(self, validated_data):
        return Product.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.productName = validated_data.get(
            "productName",
            instance.productName,
        )
        instance.description = validated_data.get(
            "description",
            instance.description,
        )
        instance.price = validated_data.get("price", instance.price)
        instance.stock = validated_data.get("stock", instance.stock)
        instance.totalStockPrice = instance.price * instance.stock
        instance.category = validated_data.get(
            "category",
            instance.category,
        )
        instance.save()
        return instance


class ProductImageVideoSerializer(AtomicSerializer):
    productName = serializers.SlugRelatedField(
        queryset=Product.objects.all(),
        slug_field='productName',
        source='product'
    )

    class Meta:
        model = ProductVideoImage
        fields = (
            "id",
            "imageUrl",
            "videoUrl",
            "processedVideoUrl",
            "thumbnail",
            "productName",
            "createdAt",
            "updatedAt"
        )
        get_fields = fields
        list_fields = fields
