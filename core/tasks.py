import requests
from celery import shared_task
from django.db.models import Sum
from django.db.models.functions import ExtractWeekDay

from mybot.serval import parse_chart_data
from myoffers.update_myoffers import update_myoffers
from myoffers.models import Myoffers
from mysales.sales_update import full_update_sales
from myoffers.utils import get_takealot_price
from users.models import User


@shared_task
def generate_sales_data(offer_id, user_id):
    offer_queryset = Myoffers.objects.filter(offer_id=offer_id, user_id=user_id)

    if offer_queryset.exists():
        my_offer = offer_queryset.first()
        sales_queryset = my_offer.mysales_set.all()

        day_of_week_mapping = {
            1: 'Mon',
            2: 'Tue',
            3: 'Wed',
            4: 'Thu',
            5: 'Fri',
            6: 'Sat',
            7: 'Sun',
        }

        all_days_of_week = [i for i in range(1, 8)]

        aggregated_sales = sales_queryset.annotate(
            day_of_week=ExtractWeekDay('order_date')
        ).values('day_of_week').annotate(
            total_quantity=Sum('quantity')
        ).order_by('day_of_week')

        sales_by_day_dict = {
            entry['day_of_week']: {'total_quantity': entry['total_quantity']} for
            entry in aggregated_sales}

        for day in all_days_of_week:
            if day not in sales_by_day_dict:
                sales_by_day_dict[day] = {'total_quantity': 0}

        sorted_sales_by_day = [sales_by_day_dict[day] for day in sorted(sales_by_day_dict.keys())]

        labels = [day_of_week_mapping.get(day, 'Unknown') for day in sorted(all_days_of_week)]
        total_quantity = [entry['total_quantity'] for entry in sorted_sales_by_day]

        data = {
            'labels': labels,
            'total_quantity': total_quantity,
        }

        return data

    else:
        return {'error': f'Offer with ID {offer_id} not found'}


def update_price(api_key, title, offer_id, new_price):
    patch_url = f"https://seller-api.takealot.com/v2/offers/offer/ID{offer_id}"
    headers = {
        'Authorization': f'Key {api_key}',
        'Content-Type': 'application/json',
    }
    payload = {
        "selling_price": new_price
    }
    response = requests.patch(patch_url, headers=headers, json=payload)
    if response.status_code == 200:
        print(f"Price for {title} updated, new price: {new_price}")
    else:
        print(f"Update error for {title}. Code: {response.status_code}")


@shared_task
def compare_prices_task():
    processed_users = set()
    myoffers = Myoffers.objects.filter(autoprice=True)
    i = 0
    for offer in myoffers:
        user = offer.user
        api_key = user.api_key
        if user.id not in processed_users:
            update_myoffers(api_key, user.id)
            get_takealot_price(user.id)
            processed_users.add(user.id)
            print(f'for user: {user.username}')
        else:
            i += 1
        new_price = offer.takealot_price - 1
        title = offer.title
        offer_id = offer.offer_id
        if offer.takealot_price < offer.selling_price and offer.takealot_price != offer.selling_price:
            if offer.min_price is not None and offer.max_price is not None and new_price > offer.min_price:
                update_price(api_key, title, offer_id, int(new_price))
            elif offer.min_price is not None and offer.max_price is not None:
                new_price = offer.max_price
                update_price(api_key, title, offer_id, int(new_price))
            else:
                print('check min/max prices')
    print(f'Miss: {i}')


@shared_task
def sales_update_task():
    users = User.objects.all()

    for user in users:
        print(user.username)
        api_key = user.api_key
        user_id = user.id
        full_update_sales(api_key, user_id)


@shared_task
def parse_chart_data_task():
    parse_chart_data()
