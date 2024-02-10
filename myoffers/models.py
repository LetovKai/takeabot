import json
import re
import time
from decimal import Decimal

import requests
from django.db import models, transaction
from fake_useragent import UserAgent
from users.models import User


class Myoffers(models.Model):
    tsin_id = models.CharField(max_length=255, db_index=True)
    image_url = models.URLField(db_index=True)
    offer_id = models.IntegerField(db_index=True)
    sku = models.CharField(max_length=255)
    barcode = models.CharField(max_length=255)
    product_label_number = models.CharField(max_length=255)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    rrp = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    leadtime_days = models.IntegerField(null=True)
    leadtime_stock = models.TextField(default="[]", blank=True, null=True)
    status = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    offer_url = models.URLField(db_index=True)
    stock_at_takealot = models.TextField(default="[]", blank=True, null=True, db_index=True)
    stock_on_way = models.TextField(default="[]", blank=True, null=True)
    total_stock_on_way = models.IntegerField(null=True)
    stock_cover = models.TextField(default="[]", blank=True, null=True)
    total_stock_cover = models.IntegerField(null=True)
    sales_units = models.IntegerField(db_index=True)
    sales_units_cpt = models.IntegerField()
    sales_units_jhb = models.IntegerField()
    stock_at_takealot_total = models.IntegerField(null=True)
    date_created = models.DateTimeField()
    storage_fee_eligible = models.BooleanField(null=True, db_index=True)
    discount = models.CharField(max_length=255)
    discount_shown = models.BooleanField()
    autoprice = models.BooleanField(default=False, null=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, db_index=True)
    takealot_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0, db_index=True)
    best_price = models.BooleanField(default=False, db_index=True)
    min_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, db_index=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    net_profit = models.IntegerField(db_index=True, null=True)
    competitors = models.IntegerField(db_index=True, null=True, default=0)
    notification_status = models.BooleanField(default=False, null=True)
    notification_message = models.TextField(blank=True, null=True)
    notification_timestamp = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = 'Myoffers'
        ordering = ['-sales_units']
        indexes = [
            models.Index(fields=['-sales_units'])
        ]
        unique_together = ('offer_id', 'user')

    def get_leadtime_stock(self):
        return json.loads(self.leadtime_stock)

    def set_leadtime_stock(self, value):
        self.leadtime_stock = json.dumps(value)

    def total_sales_units(self):
        return self.sales_units_cpt + self.sales_units_jhb

    @staticmethod
    def get_offers(user_id):
        offers = Myoffers.objects.filter(
            user_id=user_id,
        ).order_by('-stock_at_takealot_total')

        return offers



