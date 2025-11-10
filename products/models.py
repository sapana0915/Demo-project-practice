from django.db import models
from atomicloops.models import AtomicBaseModel


# Create your models here.
class Category(AtomicBaseModel):
    categoryName = models.CharField(max_length=255,
                                    verbose_name="Category Name",
                                    unique=True,
                                    db_column="category_name")

    description = models.TextField(verbose_name="Description", null=True,
                                   db_column="description")

    def __str__(self):
        return self.categoryName


class Product(AtomicBaseModel):
    productName = models.CharField(max_length=255,
                                   verbose_name="Product Name",
                                   db_column="product_name",
                                   db_index=True,
                                   null=True
                                   )

    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products_category',
                                 verbose_name="Category",
                                 db_column="category_id",
                                 db_index=True,
                                 )

    description = models.TextField(
                                verbose_name="Description",
                                null=True,
                                db_column="description")

    price = models.DecimalField(
                                max_digits=10,
                                decimal_places=2,
                                verbose_name="Price",
                                db_column="price",
                                db_index=True,
                                )

    stock = models.PositiveIntegerField(
                                verbose_name="Stock",
                                db_column="stock",
                                db_index=True,
                                )

    totalStockPrice = models.DecimalField(
                                max_digits=15,
                                verbose_name="Total Stock Price",
                                decimal_places=2,
                                db_column="total_stock_price",
                                db_index=True,
                                null=True,
                                )

    def __str__(self):
        return self.productName

    def save(self, *args, **kwargs):
        if self.price and self.stock is not None:
            self.totalStockPrice = self.price * self.stock
        super().save(*args, **kwargs)


class ProductVideoImage(AtomicBaseModel):
    imageUrl = models.FileField(max_length=500,
                                verbose_name="Image URL",
                                db_column="image_url",
                                db_index=True,
                                null=True
                                )
    videoUrl = models.FileField(max_length=500,
                                verbose_name="Video URL",
                                db_column="video_url",
                                db_index=True,
                                null=True,
                                upload_to='videos/originals/'
                                )
    processedVideoUrl = models.FileField(
        max_length=500,
        verbose_name="Processed Video URL",
        db_column="processed_video_url",
        db_index=True,
        null=True,
        upload_to='videos/processed/'
    )
    thumbnail = models.ImageField(
        max_length=500,
        verbose_name="Video Thumbnail",
        db_column="video_thumbnail",
        db_index=True,
        null=True,
        upload_to='videos/thumbnails/'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images_product',
                                verbose_name="Product",
                                db_column="product_id",
                                db_index=True,
                                )

    def __str__(self):
        if self.imageUrl:
            return str(self.imageUrl)
        if self.videoUrl:
            return str(self.videoUrl)
        return str(self.id)


class comment(AtomicBaseModel):
    commentText = models.CharField(max_length=255,
                                   verbose_name="Comment Text",
                                   db_column="comment_text",
                                   db_index=True,
                                   null=True
                                   )
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='comments_product',
                                verbose_name="Product",
                                db_column="product_id",
                                db_index=True,
                                )

    def __str__(self):
        return self.commentText
