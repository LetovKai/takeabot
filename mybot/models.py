from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    tsin = models.CharField(max_length=100, null=True)
    url = models.URLField()
    category = models.CharField(max_length=50)
    brand = models.CharField(max_length=50)
    brand_url = models.URLField()
    name = models.CharField(max_length=550)
    review = models.IntegerField()
    rating = models.DecimalField(max_digits=5, decimal_places=2)
    price = models.IntegerField()
    img = models.URLField()

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ['-review']
        indexes = [
            models.Index(fields=['-review'])
        ]


class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    price = models.IntegerField()
    review = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.product} - {self.timestamp} - {self.price}'
