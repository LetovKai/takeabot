from django.db import models
from django.db.models import Sum, F, Count, FloatField, ExpressionWrapper, DecimalField, Q, When, Value, Case, Avg
from django.db.models.functions import TruncDate, Round, TruncHour

from mybot.models import Product
from myoffers.models import Myoffers
from mysales.forms import DateRangeService
from users.models import User


class Mysales(models.Model):
    order_item_id = models.IntegerField()
    order_id = models.IntegerField(db_index=True)
    order_date = models.DateTimeField(db_index=True)
    sale_status = models.CharField(max_length=255, db_index=True)
    offer_id = models.IntegerField()
    tsin = models.CharField(max_length=255)
    sku = models.CharField(max_length=255)
    product_title = models.CharField(max_length=255, db_index=True)
    takealot_url_mobi = models.URLField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    quantity = models.IntegerField(db_index=True)
    dc = models.CharField(max_length=255, db_index=True)
    customer = models.CharField(max_length=255, db_index=True)
    takealot_url = models.URLField()
    success_fee = models.DecimalField(max_digits=10, decimal_places=2)
    fulfillment_fee = models.DecimalField(max_digits=10, decimal_places=2)
    courier_collection_fee = models.DecimalField(max_digits=10, decimal_places=2)
    auto_ibt_fee = models.DecimalField(max_digits=10, decimal_places=2)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2)
    myoffer = models.ForeignKey(Myoffers, null=True, on_delete=models.CASCADE, db_index=True)
    decimal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Mysales #{self.product_title}'

    class Meta:
        verbose_name_plural = 'Mysales'
        ordering = ['-order_date']
        indexes = [
            models.Index(fields=['-order_date'])
        ]
        unique_together = ('order_item_id', 'user')

    @staticmethod
    def get_sales(sale_filter, user_id, start_date, end_date):
        if start_date is None and end_date is None:
            start_date, end_date = DateRangeService.get_date_range(sale_filter)

        cancelation_statuses = [
            'Cancelled by Customer', 'Cancelled by Takealot',
            'Cancelled by Takealot - DC Stock Inquiry', 'Cancelled - Late Delivery',
            'Cancelled by Customer', 'Cancelled - Inbound Exception', 'Returned',
        ]

        sales = Mysales.objects.filter(
            order_date__date__range=[start_date, end_date],
            user_id=user_id
        ).exclude(
            Q(sale_status__in=cancelation_statuses)
        )

        sales_data = sales.aggregate(
            sales_amount=Sum('selling_price'),
            sales_units=Sum('quantity'),
            sales_total=Count('quantity'),
            average_sale_amount=Round(Avg('selling_price'), 2)
        )
        return {
            'sales_amount': sales_data['sales_amount'],
            'sales_total': sales_data['sales_total'],
            'sales_units': sales_data['sales_units'],
            'average_sale_amount': sales_data['average_sale_amount'],
        }

    @staticmethod
    def get_returns(ret_filter, user_id, start_date, end_date):
        if start_date is None and end_date is None:
            start_date, end_date = DateRangeService.get_date_range(ret_filter)
        returns = Mysales.objects.filter(
            order_date__date__range=[start_date, end_date],
            sale_status='Returned',
            user_id=user_id
        )

        returns_data = returns.aggregate(
            return_total=Count('id'),
            return_amount=Sum('selling_price'),
            return_units=Sum('quantity'),
            return_total_fee_sum=Sum(F('auto_ibt_fee') + F('fulfillment_fee')) or 0
        )

        return {
            'return_total': returns_data['return_total'],
            'return_amount': returns_data['return_amount'],
            'return_units': returns_data['return_units'],
            'return_total_fee_sum': returns_data['return_total_fee_sum'],
        }

    @staticmethod
    def get_cancelations(can_filter, user_id, start_date, end_date):
        if start_date is None and end_date is None:
            start_date, end_date = DateRangeService.get_date_range(can_filter)
        cancelations = Mysales.objects.filter(
            order_date__date__range=[start_date, end_date],
            user_id=user_id,
            sale_status__in=[
                'Cancelled by Customer',
                'Cancelled by Takealot',
                'Cancelled by Takealot - DC Stock Inquiry',
                'Cancelled - Late Delivery',
                'Cancelled by Customer',
                'Cancelled - Inbound Exception',
            ]
        )

        cancelations_data = cancelations.aggregate(
            cancelations_total=Count('id'),
            cancelations_amount=Sum('selling_price'),
            cancelations_units=Sum('quantity'),
            cancelations_total_fee_sum=Sum('total_fee') or 0,
        )

        return {
            'cancelations_total': cancelations_data['cancelations_total'],
            'cancelations_amount': cancelations_data['cancelations_amount'],
            'cancelations_units': cancelations_data['cancelations_units'],
            'cancelations_total_fee_sum': cancelations_data['cancelations_total_fee_sum'],
        }

    @staticmethod
    def get_chart_data(filter_type, user_id, start_date, end_date):
        if start_date is None and end_date is None:
            start_date, end_date = DateRangeService.get_date_range(filter_type)
        sales_queryset = Mysales.objects.filter(order_date__date__range=[start_date, end_date], user=user_id)

        if start_date == end_date:
            chart_data = sales_queryset.annotate(date=TruncHour('order_date')).values('date').annotate(
                total_value=Sum('selling_price'),
                returned_value=Sum(Case(
                    When(sale_status='Returned', then=F('selling_price')),
                    default=Value(0),
                    output_field=DecimalField()
                )),
                cancelled_value=Sum(Case(
                    When(sale_status__in=['Cancelled by Customer', 'Cancelled by Takealot',
                                          'Cancelled by Takealot - DC Stock Inquiry', 'Cancelled - Late Delivery',
                                          'Cancelled by Customer', 'Cancelled - Inbound Exception'],
                         then=F('selling_price')),
                    default=Value(0),
                    output_field=DecimalField()
                ))
            ).order_by('date')
            chart_dates = [entry['date'].strftime('%Y-%m-%d %H:%M:%S') for entry in chart_data]
        else:
            chart_data = sales_queryset.annotate(date=TruncDate('order_date')).values('date').annotate(
                total_value=Sum('selling_price'),
                returned_value=Sum(Case(
                    When(sale_status='Returned', then=F('selling_price')),
                    default=Value(0),
                    output_field=DecimalField()
                )),
                cancelled_value=Sum(Case(
                    When(sale_status__in=['Cancelled by Customer', 'Cancelled by Takealot',
                                          'Cancelled by Takealot - DC Stock Inquiry', 'Cancelled - Late Delivery',
                                          'Cancelled by Customer', 'Cancelled - Inbound Exception'],
                         then=F('selling_price')),
                    default=Value(0),
                    output_field=DecimalField()
                ))
            ).order_by('date')
            chart_dates = [entry['date'].strftime('%Y-%m-%d') for entry in chart_data]

        chart_values = [
            {
                'total_value': float(entry['total_value']),
                'returned_value': float(entry['returned_value']),
                'cancelled_value': float(entry['cancelled_value'])
            }
            for entry in chart_data
        ]
        return chart_dates, chart_values

    @staticmethod
    def recent_sales(filter_type, user_id, checkboxes, start_date, end_date):
        if start_date is None and end_date is None:
            start_date, end_date = DateRangeService.get_date_range(filter_type)
        recent_sales_query = Mysales.objects.filter(
            order_date__date__range=[start_date, end_date],
            user_id=user_id
        )
        cancelation_statuses = [
            'Cancelled by Customer', 'Cancelled by Takealot',
            'Cancelled by Takealot - DC Stock Inquiry', 'Cancelled - Late Delivery',
            'Cancelled by Customer', 'Cancelled - Inbound Exception',
        ]

        city_conditions = Q()
        status_conditions = Q()

        if checkboxes['cpt']:
            city_conditions |= Q(dc='CPT')
        if checkboxes['jhb']:
            city_conditions |= Q(dc='JHB')

        if checkboxes['returned']:
            status_conditions |= Q(sale_status='Returned')
        if checkboxes['cancelations']:
            status_conditions |= Q(sale_status__in=cancelation_statuses)

        if city_conditions and status_conditions:
            recent_sales_query = recent_sales_query.filter(city_conditions & status_conditions)
        elif city_conditions:
            recent_sales_query = recent_sales_query.filter(city_conditions)
        elif status_conditions:
            recent_sales_query = recent_sales_query.filter(status_conditions)

        recent_sales_query = recent_sales_query.values(
            'order_date', 'sale_status', 'order_id', 'takealot_url',
            'product_title', 'selling_price', 'quantity', 'customer',
            'tsin', 'dc', 'success_fee', 'fulfillment_fee', 'courier_collection_fee',
            'auto_ibt_fee', 'total_fee', 'net_profit', 'myoffer__offer_id', 'myoffer_id', 'order_item_id'
        ).annotate(
            cost_price=F('myoffer__cost_price') * F('quantity'),
            decimal=F('net_profit') - F('cost_price'),
            pure_profit=Case(
                When(sale_status__in=cancelation_statuses, then=Value(0) - F('total_fee')),
                When(sale_status='Returned', then=Value(0) - F('fulfillment_fee') - F('auto_ibt_fee')),
                When(sale_status='Shipped to Customer',
                     then=ExpressionWrapper(F('net_profit') - (F('myoffer__cost_price') * F('quantity')),
                                            output_field=DecimalField())),
                default=Value(0),
                output_field=DecimalField()
            )
        ).order_by('-order_date')

        exclude_statuses = cancelation_statuses + ['Returned']
        cost_price_query = recent_sales_query.exclude(sale_status__in=exclude_statuses)

        aggregation = recent_sales_query.aggregate(
            total_fee=Sum('total_fee'),
            total_pure_profit=Sum('pure_profit')
        )
        cost_price_aggregation = cost_price_query.aggregate(
            total_cost_price=Sum('cost_price')
        )

        total_cost_price = cost_price_aggregation['total_cost_price'] or 0
        total_fee = aggregation['total_fee'] or 0
        total_pure_profit = aggregation['total_pure_profit'] or 0
        total_sum = total_cost_price + total_fee + total_pure_profit
        cost_price_percentage = round((total_cost_price / total_sum) * 100, 2) if total_sum != 0 else 0
        fee_percentage = round((total_fee / total_sum) * 100, 2) if total_sum != 0 else 0
        pure_profit_percentage = round((total_pure_profit / total_sum) * 100, 2) if total_sum != 0 else 0

        recent_sales = []
        for sale in recent_sales_query:
            formatted_date = sale['order_date'].strftime("%d.%m %H:%M")
            sale['formatted_order_date'] = formatted_date
            recent_sales.append(sale)

        myoffer_conditions = Q(myoffer__status='Buyable') | Q(myoffer__status='Not Buyable')
        all_cost_prices = Mysales.objects.filter(myoffer_conditions, myoffer__cost_price=None).exists()
        return recent_sales, total_pure_profit, total_fee, total_cost_price, all_cost_prices, cost_price_percentage, fee_percentage, pure_profit_percentage

    @staticmethod
    def top_sales(filter_type, api_key, user_id):
        # start_date, end_date = DateRangeService.get_date_range(filter_type)
        sales_data_quantity = Mysales.objects.filter(
            user_id=user_id).values('offer_id').annotate(total_quantity=Sum('quantity')).order_by('offer_id')
        total_money_data = Mysales.objects.filter(
            user_id=user_id).values('offer_id').annotate(total_money=Sum('selling_price')).order_by(
            'offer_id')
        offers_data = Myoffers.objects.filter(
            user_id=user_id).values('offer_id', 'image_url', 'stock_at_takealot_total')
        offers_data_dict = {int(item['offer_id']): item for item in offers_data}
        top_sales = Mysales.objects.filter(
            user_id=user_id,
            # order_date__date__range=[start_date, end_date]
        ).values(
            'offer_id', 'product_title', 'takealot_url'
        )

        combined_data = {}
        for data in sales_data_quantity:
            combined_data[data['offer_id']] = data
        for data in total_money_data:
            combined_data[data['offer_id']].update(data)
        for data in offers_data:
            offer_id = int(data['offer_id'])
            if offer_id in combined_data:
                combined_data[offer_id].update(data)
        for sale in top_sales:
            offer_id = sale['offer_id']
            if offer_id in combined_data:
                combined_data[offer_id].update(sale)
            if offer_id in offers_data_dict:
                combined_data[offer_id].update(offers_data_dict[offer_id])

            if 'total_money' in combined_data[offer_id] and combined_data[offer_id]['total_quantity'] > 0:
                price = round(combined_data[offer_id]['total_money'] / combined_data[offer_id]['total_quantity'], 2)
                combined_data[offer_id]['price'] = price
            else:
                combined_data[offer_id]['price'] = 0

        sorted_combined_data = sorted(combined_data.values(), key=lambda x: x.get('total_money', 0), reverse=True)
        return sorted_combined_data[:5]
