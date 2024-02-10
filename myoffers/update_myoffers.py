import time

import requests
from django.utils.dateparse import parse_datetime
import pytz
from myoffers.models import Myoffers
from users.models import User


def update_myoffers_script(api_key, user_id):
    headers = {
        'Authorization': f'Key {api_key}',
        'Content-Type': 'application/json',
    }
    offers_url = 'https://seller-api.takealot.com/v2/offers'
    page_number = 1
    page_size = 100
    while True:
        params = {'page_size': page_size, 'page_number': page_number}
        response = requests.get(offers_url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json().get('offers', [])
            if not data:
                break
            for offers_data in data:
                offer_id = offers_data['offer_id']
                sales_units_data = offers_data['sales_units']
                sales_units_cpt = 0
                sales_units_jhb = 0
                for item in sales_units_data:
                    warehouse_id = item['warehouse_id']
                    if warehouse_id == 1:
                        sales_units_cpt += item['sales_units']
                    elif warehouse_id == 3:
                        sales_units_jhb += item['sales_units']
                sales_units = sales_units_cpt + sales_units_jhb
                date_created_str = offers_data['date_created']
                date_created_naive = parse_datetime(date_created_str)
                date_created_aware = pytz.UTC.localize(date_created_naive)

                defaults = {
                    'tsin_id': offers_data['tsin_id'],
                    'image_url': offers_data['image_url'],
                    'sku': offers_data['sku'],
                    'barcode': offers_data['barcode'],
                    'product_label_number': offers_data['product_label_number'],
                    'selling_price': offers_data['selling_price'],
                    'rrp': offers_data['rrp'],
                    'leadtime_days': offers_data['leadtime_days'],
                    'leadtime_stock': offers_data['leadtime_stock'],
                    'status': offers_data['status'],
                    'title': offers_data['title'],
                    'offer_url': offers_data['offer_url'],
                    'stock_at_takealot': offers_data['stock_at_takealot'],
                    'stock_on_way': offers_data['stock_on_way'],
                    'total_stock_on_way': offers_data['total_stock_on_way'],
                    'stock_cover': offers_data['stock_cover'],
                    'total_stock_cover': offers_data['total_stock_cover'],
                    'sales_units': sales_units,
                    'sales_units_cpt': sales_units_cpt,
                    'sales_units_jhb': sales_units_jhb,
                    'stock_at_takealot_total': offers_data['stock_at_takealot_total'],
                    'date_created': date_created_aware,
                    'storage_fee_eligible': offers_data['storage_fee_eligible'],
                    'discount': offers_data['discount'],
                    'discount_shown': offers_data['discount_shown'],
                    'user_id': user_id,
                }

                Myoffers.objects.update_or_create(
                    offer_id=offer_id,
                    user_id=user_id,
                    defaults=defaults
                )
            page_number += 1
        else:
            print(f"Failed to fetch data from the API. Status code: {response.status_code}")
            break

    return response.status_code


def update_myoffers(api_key, user_id):
    start_time = time.time()
    response_status_code = update_myoffers_script(api_key, user_id)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"script update_myoffers take {execution_time} sec.")
    return response_status_code


if __name__ == '__main__':
    update_myoffers()