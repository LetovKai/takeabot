import pytz
import requests

from django.utils.dateparse import parse_datetime

from myoffers.models import Myoffers
from .models import Mysales
from datetime import datetime


def save_sales_to_database(api_key, user_id, start_date):
    existing_order_ids = set(Mysales.objects.filter(user_id=user_id).values_list('order_item_id', flat=True))
    page_number = 1
    page_size = 100
    new_sales_objs = []
    updated_sales_objs = []
    url = 'https://seller-api.takealot.com/v2/sales'
    headers = {
        'Authorization': f'Key {api_key}',
        'Content-Type': 'application/json',
    }
    while True:
        filter_str = f'start_date:{start_date}'
        params = {
            'page_size': page_size,
            'page_number': page_number,
            'filters': filter_str
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get('sales', [])
            if not data:
                break
            for sale_data in data:
                sale_key = f"{sale_data['sale_status']}_{sale_data['total_fee']}_{sale_data['order_id']}_{sale_data['tsin']}_{user_id}"
                offer_id = sale_data['offer_id']

                date_str = sale_data['order_date']
                date_obj = datetime.strptime(date_str, "%d %b %Y %H:%M:%S")
                order_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                date_created_naive = parse_datetime(order_date)
                date_created_aware = pytz.UTC.localize(date_created_naive)

                net_profit = sale_data['selling_price'] - sale_data['total_fee']
                try:
                    myoffer = Myoffers.objects.get(user_id=user_id, offer_id=offer_id)
                except Myoffers.DoesNotExist:
                    myoffer = None

                if myoffer is None:
                    break
                decimal = 0

                sale = {
                    'order_item_id': sale_data['order_item_id'],
                    'order_id': sale_data['order_id'],
                    'order_date': date_created_aware,
                    'sale_status': sale_data['sale_status'],
                    'offer_id': sale_data['offer_id'],
                    'tsin': sale_data['tsin'],
                    'sku': sale_data['sku'],
                    'product_title': sale_data['product_title'],
                    'takealot_url_mobi': sale_data['takealot_url_mobi'],
                    'selling_price': sale_data['selling_price'],
                    'quantity': sale_data['quantity'],
                    'dc': sale_data['dc'],
                    'customer': sale_data['customer'],
                    'takealot_url': sale_data['takealot_url'],
                    'success_fee': sale_data['success_fee'],
                    'fulfillment_fee': sale_data['fulfillment_fee'],
                    'courier_collection_fee': sale_data['courier_collection_fee'],
                    'auto_ibt_fee': sale_data['auto_ibt_fee'],
                    'total_fee': sale_data['total_fee'],
                    'user_id': user_id,
                    'net_profit': net_profit,
                    'myoffer': myoffer,
                    'decimal': decimal,
                }

                if sale['order_item_id'] in existing_order_ids:
                    existing_obj = Mysales.objects.get(order_item_id=sale_data['order_item_id'], user_id=user_id)
                    for key, value in sale.items():
                        setattr(existing_obj, key, value)
                    updated_sales_objs.append(existing_obj)
                else:
                    new_sales_objs.append(Mysales(**sale))
            page_number += 1
        else:
            if response.status_code == 401:
                print(f"Error. Code: {response.status_code}, check ApiKey")
                return response.status_code
            else:
                print(f"Error. Code: {response.status_code}")
                return response.status_code
    Mysales.objects.bulk_create(new_sales_objs)
    Mysales.objects.bulk_update(updated_sales_objs,
                                ['sale_status', 'selling_price', 'success_fee', 'fulfillment_fee',
                                 'courier_collection_fee', 'auto_ibt_fee', 'total_fee', 'net_profit', ])
    return response.status_code
