from django.contrib import admin

from .models import Product, PriceHistory


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'review', 'price', 'img')
    ordering = ['-review', '-price']


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'timestamp', 'price')
    ordering = ['-timestamp']
