import requests
from django.db import transaction
from fake_useragent import UserAgent
import time

from myoffers.models import Myoffers
from .models import Product, PriceHistory
import re
from celery import shared_task


def category():
    ua = UserAgent()
    url = 'https://api.takealot.com/rest/v-1-11-0/cms/merchandised-departments?display_only=True'
    resp = requests.get(url, headers={'user-agent': f'{ua.random}'})
    data = resp.json()
    items = data.get('merchandised_departments')
    cat = []

    for i in items:
        c = i.get('slug')
        if c and c.lower() not in ():
            cat.append(c)
    return cat


def collect_data(cate):
    ua = UserAgent()
    aft = None
    print(f'start: {cate}')
    counter = 0
    while True:
        url = ('https://api.takealot.com/rest/v-1-11-0/searches/products,filters,facets,sort_options,breadcrumbs,'
               'slots_audience,context,seo')
        params = {
            'after': aft,
            'sort': 'Relevance',
            'department_slug': cate,
        }
        resp = requests.get(url, headers={'user-agent': f'{ua.random}'}, params=params)
        data = resp.json()
        items = data.get('sections', {}).get('products', {}).get('results')
        if items is not None:
            for i in items:
                id = i.get('product_views', {}).get('core', {}).get('id')
                tsin_id = i.get('product_views', {}).get('buybox_summary', {}).get('tsin')
                item_full_name = i.get('product_views', {}).get('core', {}).get('title')
                item_url = 'https://www.takealot.com/' + i.get('product_views', {}).get('core', {}).get('slug')
                review = i.get('product_views', {}).get('core', {}).get('reviews')
                rating = i.get('product_views', {}).get('core', {}).get('star_rating')
                price_str = i.get('product_views', {}).get('buybox_summary', {}).get('pretty_price')
                digits = re.sub(r'\D', '', price_str)
                try:
                    price = int(digits)
                except ValueError:
                    price = 0
                img_link = i.get('product_views', {}).get('gallery', {}).get('images')
                img_url = [link.replace("{size}", "fb")
                           for link in img_link][0] if isinstance(img_link, list) and img_link else img_link
                brand_name = i.get('product_views', {}).get('core', {}).get('brand')
                if brand_name is not None:
                    brand_link = 'https://www.takealot.com' + i.get('product_views', {}).get('core', {}).get(
                        'brand_url', {}).get('link_data', {}).get('path')
                    brand_fields = i.get('product_views', {}).get('core', {}).get('brand_url', {}).get('link_data',
                                                                                                       {}).get('fields',
                                                                                                               {}).get(
                        'brand_slug')
                    brand_url = brand_link.replace("{brand_slug}", brand_fields)
                else:
                    brand_url = 'https://www.takealot.com'
                    brand_name = 'None brand'

                product, created = Product.objects.get_or_create(id=id, defaults={
                    'tsin': tsin_id,
                    'url': item_url + '/PLID' + str(id),
                    'category': cate,
                    'brand': brand_name,
                    'brand_url': brand_url,
                    'name': item_full_name,
                    'review': review,
                    'rating': rating,
                    'price': int(price),
                    'img': img_url
                })

                if not created:
                    product.review = review
                    product.rating = rating
                    product.price = int(price)

                    product.save()

                PriceHistory.objects.create(product=product, price=price, review=review)

            aft = data.get('sections', {}).get('products', {}).get('paging', {}).get('next_is_after')
            counter += 1
            # print(f"\rDone page: {counter}, code: {resp.status_code}", end='', flush=True)
            # time.sleep(3)
        else:

            break


@shared_task
def parse_all():
    cat = category()
    for el in cat:
        cate = el
        collect_data(cate)
        print(cate + " Done")


@shared_task
def parse_category():
    cate = 'computers'
    collect_data(cate)
