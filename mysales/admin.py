from django.contrib import admin

from .models import Mysales


@admin.register(Mysales)
class MysalesAdmin(admin.ModelAdmin):
    list_display = ('order_date', 'user', 'net_profit', 'product_title', 'selling_price', 'quantity', 'sale_status')
    ordering = ['-order_date']
