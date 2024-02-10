from django.contrib import admin

from .models import Myoffers


@admin.register(Myoffers)
class MysalesAdmin(admin.ModelAdmin):
    list_display = ('title', 'selling_price', 'user', 'offer_url', 'takealot_price', 'autoprice', 'status', 'sales_units', 'max_price', 'min_price', 'stock_at_takealot_total',)
    ordering = ['-sales_units']
