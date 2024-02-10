import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from mybot.models import Product, PriceHistory
import time
from celery import shared_task


@shared_task()
def parse_chart_data():
    products = Product.objects.filter(review__lt=52)
    for product in products:
        print(product.review)
        url = product.url
        parts = url.split('/')
        plid = None
        for part in parts:
            if part.startswith("PLID"):
                plid = part
                break
        if plid:
            serval_url = f"https://www.servaltracker.com/products/{plid}/"

        response = requests.get(serval_url)
        time.sleep(1)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            chart_scripts = soup.find_all('script', {'type': 'text/javascript'})

            if len(chart_scripts) >= 9:
                chart_script = chart_scripts[8]
                data_string = chart_script.contents[0]
                start_index = data_string.find('data = ') + len('data = ')
                end_index = data_string.find('var ctx = $("#chart")')
                json_data = data_string[start_index:end_index].strip()
                try:
                    data = json.loads(json_data)
                    labels = [datetime.utcfromtimestamp(label / 1000).strftime('%Y-%m-%d %H:%M:%S') for label in
                              data['labels']]
                    prices = data['datasets'][0]['data']

                    for label, price in zip(labels, prices):
                        PriceHistory.objects.create(product=product, timestamp=label, price=price)

                except json.JSONDecodeError as e:
                    print(f'Ошибка при загрузке данных JSON: {e}')
                    print(f'Содержимое скрипта: {json_data}')
            if not chart_scripts:
                print('Скрипты с данными графика не найдены.')
        else:
            print(f'Ошибка при отправке запроса: {response.status_code}')




