import re
from decimal import Decimal

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum, Avg, F
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View

from core.tasks import update_price, generate_sales_data
from mybot.models import Product
from myoffers.models import Myoffers
from myoffers.update_myoffers import update_myoffers
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.loader import render_to_string

from myoffers.utils import compare_prices, get_takealot_price, get_takealot_one_price


def edit_offer(request):  # edit form for card

    if request.method == 'POST':
        sale_id = request.POST.get('id')
        min_price_str = request.POST.get('min_price')
        max_price_str = request.POST.get('max_price')

        if min_price_str and max_price_str:
            min_price = int(min_price_str)
            max_price = int(max_price_str)

            if min_price > max_price:
                return HttpResponse(
                    '<div style="color: red; padding: 10px;">Maximum price must equal or exceed Min price</div>')
        else:
            min_price = None
            max_price = None
        cost_price = request.POST.get('cost_price')
        selling_price = request.POST.get('selling_price')
        api_key = request.user.api_key
        try:
            offer = Myoffers.objects.get(id=sale_id)
            offer_title = offer.title
            offer_id = offer.offer_id
            if cost_price is not None and cost_price != '':
                offer.cost_price = cost_price
            if min_price is not None and min_price != '':
                offer.min_price = min_price
            if max_price is not None and max_price != '':
                offer.max_price = max_price
            if selling_price is not None and selling_price != '':
                selling_price = int(selling_price)
                offer.selling_price = selling_price
                update_price(api_key, offer_title, offer_id, selling_price)
            print(offer.cost_price)
            offer.save()
            context = {
                'message': 'Offer updated successfully',

            }
            return render(request, 'partials/edit_close.html', context)
        except Myoffers.DoesNotExist:
            return HttpResponse('Error')

    return HttpResponse('Error')


def upd_offers(request):
    api_key = request.user.api_key
    user_id = request.user.id
    update_myoffers(api_key, user_id)
    compare_prices()
    redirect_url = request.META.get('HTTP_REFERER', reverse_lazy('myoffers:myoffers'))
    response = JsonResponse({'status': 'success'})
    response['HX-Redirect'] = redirect_url
    return response


def upd_market_price(request):
    api_key = request.user.api_key
    user_id = request.user.id
    update_myoffers(api_key, user_id)
    get_takealot_price(user_id)
    redirect_url = request.META.get('HTTP_REFERER', reverse_lazy('myoffers:myoffers'))
    response = JsonResponse({'status': 'success'})
    response['HX-Redirect'] = redirect_url
    return response


def upd_one_market_price(request, offer_id):
    user_id = request.user.id
    get_takealot_one_price(user_id, offer_id)
    redirect_url = request.META.get('HTTP_REFERER', reverse_lazy('myoffers:myoffers'))
    return JsonResponse({'status': 'success', 'redirect_url': redirect_url})


def toggle_autoprice(request, sale_id):
    sale = get_object_or_404(Myoffers, id=sale_id)
    if not request.user.status:
        if sale.autoprice is True:
            request.user.autoprice += 1
            request.user.save()
        else:
            if request.user.autoprice <= 0:
                return JsonResponse({'error': 'Not enough autoprice tokens'}, status=400)
            else:
                request.user.autoprice -= 1
                request.user.save()
    sale.autoprice = not sale.autoprice
    sale.save()

    context = {'sale': sale}
    html = render_to_string('partials/autoprice_button.html', context, request=request)
    return HttpResponse(html)


class MyoffersListView(LoginRequiredMixin, View):
    template_name = 'myoffers/myoffers.html'
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        offers_data = Myoffers.objects.prefetch_related('mysales_set').filter(user_id=user_id)

        buybox_checked = request.GET.get('buybox')
        fee_checked = request.GET.get('fee')
        profit_checked = request.GET.get('profit')
        best_checked = request.GET.get('best')
        cost_checked = request.GET.get('cost')
        buy_checked = request.GET.get('buy')
        dbt_checked = request.GET.get('dbt')
        nbuy_checked = request.GET.get('nbuy')
        dbs_checked = request.GET.get('dbs')
        active_checked = request.GET.get('active')
        inactive_checked = request.GET.get('inactive')
        minmax_checked = request.GET.get('minmax')
        suff_checked = request.GET.get('suff')
        low_checked = request.GET.get('low')
        out_checked = request.GET.get('out')
        sort_param = request.GET.get('sort', 'default')
        paginate_by = request.GET.get('paginate_by', self.paginate_by)

        if buy_checked is None and nbuy_checked is None and dbt_checked is None and dbs_checked is None:
            buy_checked = True
            nbuy_checked = True

        for offer in offers_data:
            sales = offer.mysales_set.all()
            total_price = sum(sale.selling_price for sale in sales)
            total_quantity = sum(sale.quantity for sale in sales)

            if total_quantity > 0:
                average_price = round(total_price / total_quantity, 2)
            else:
                average_price = None

            total_profit = None

            for sale in sales:
                if sale.total_fee is not None:
                    offer.fee = (sale.total_fee - sale.auto_ibt_fee) / sale.quantity
                    if offer.cost_price is not None:
                        offer.net_profit = round(offer.selling_price - offer.fee - offer.cost_price, 2)
                        total_quantity_decimal = Decimal(total_quantity)
                        total_profit = total_quantity_decimal * offer.net_profit

            offer.average_price = average_price
            offer.sales_total_all = total_quantity
            offer.total_price = total_price
            offer.total_profit = total_profit

        if buy_checked or dbt_checked or nbuy_checked or dbs_checked:
            offers_data = [offer for offer in offers_data if
                           (buy_checked and offer.status == 'Buyable') or
                           (dbt_checked and offer.status == 'Disabled by Takealot') or
                           (nbuy_checked and offer.status == 'Not Buyable') or
                           (dbs_checked and offer.status == 'Disabled by Seller')]

        if suff_checked or low_checked or out_checked:
            offers_data = [offer for offer in offers_data if
                           (suff_checked and offer.stock_at_takealot_total > 5) or
                           (low_checked and 0 < offer.stock_at_takealot_total <= 5) or
                           (out_checked and offer.stock_at_takealot_total == 0)]

        if buybox_checked:
            offers_data = [offer for offer in offers_data if offer.selling_price > offer.takealot_price]
        if fee_checked:
            offers_data = [offer for offer in offers_data if offer.storage_fee_eligible]
        if profit_checked:
            offers_data = [offer for offer in offers_data if
                           offer.net_profit and Decimal(offer.net_profit) <= Decimal('21')]
        if cost_checked:
            offers_data = [offer for offer in offers_data if offer.cost_price is None]
        if minmax_checked:
            offers_data = [offer for offer in offers_data if not (offer.min_price and offer.max_price)]

        if active_checked:
            if inactive_checked:
                pass
            else:
                offers_data = [offer for offer in offers_data if offer.autoprice]
        if inactive_checked:
            if active_checked:
                pass
            else:
                offers_data = [offer for offer in offers_data if not offer.autoprice]

        if sort_param == 'sales_unit_up':
            offers_data = sorted(offers_data, key=lambda x: sum(sale.quantity for sale in x.mysales_set.all()),
                                 reverse=True)
        elif sort_param == 'sales_unit_down':
            offers_data = sorted(offers_data, key=lambda x: sum(sale.quantity for sale in x.mysales_set.all()),
                                 reverse=False)
        if sort_param == 'sales_revenue_up':
            offers_data = sorted(offers_data, key=lambda x: sum(sale.selling_price for sale in x.mysales_set.all()),
                                 reverse=True)
        if sort_param == 'sales_revenue_down':
            offers_data = sorted(offers_data, key=lambda x: sum(sale.selling_price for sale in x.mysales_set.all()),
                                 reverse=False)
        if sort_param == 'profit_up':
            offers_data = sorted(offers_data, key=lambda x: x.total_profit if x.total_profit is not None else 0,
                                 reverse=True)
        if sort_param == 'profit_down':
            offers_data = sorted(offers_data, key=lambda x: x.total_profit if x.total_profit is not None else 0,
                                 reverse=False)
        if sort_param == 'add_date_up':
            offers_data = sorted(offers_data, key=lambda x: x.date_created, reverse=False)
        if sort_param == 'add_date_down':
            offers_data = sorted(offers_data, key=lambda x: x.date_created, reverse=True)

        if sort_param == 'title_up':
            offers_data = sorted(offers_data, key=lambda x: x.title, reverse=False)
        if sort_param == 'title_down':
            offers_data = sorted(offers_data, key=lambda x: x.title, reverse=True)

        if sort_param == 'selling_price_up':
            offers_data = sorted(offers_data, key=lambda x: x.selling_price if x.selling_price is not None else 0,
                                 reverse=True)
        if sort_param == 'selling_price_down':
            offers_data = sorted(offers_data, key=lambda x: x.selling_price if x.selling_price is not None else 0,
                                 reverse=False)

        if sort_param == 'stock_up':
            offers_data = sorted(offers_data, key=lambda
                x: x.stock_at_takealot_total if x.stock_at_takealot_total is not None else 0, reverse=True)
        if sort_param == 'stock_down':
            offers_data = sorted(offers_data, key=lambda
                x: x.stock_at_takealot_total if x.stock_at_takealot_total is not None else 0, reverse=False)

        self.paginate_by = paginate_by
        paginator = Paginator(offers_data, self.paginate_by)
        page = request.GET.get('page')

        try:
            offers_data = paginator.page(page)
        except PageNotAnInteger:
            offers_data = paginator.page(1)
        except EmptyPage:
            offers_data = None

        context = {
            'offers_data': offers_data,
            'buybox_checked': buybox_checked,
            'fee_checked': fee_checked,
            'profit_checked': profit_checked,
            'best_checked': best_checked,
            'cost_checked': cost_checked,
            'buy_checked': buy_checked,
            'dbt_checked': dbt_checked,
            'nbuy_checked': nbuy_checked,
            'dbs_checked': dbs_checked,
            'active_checked': active_checked,
            'inactive_checked': inactive_checked,
            'minmax_checked': minmax_checked,
            'suff_checked': suff_checked,
            'low_checked': low_checked,
            'out_checked': out_checked,
            'total_price': sum(sale.selling_price for sale in sales),
            'sort_param': sort_param,
        }

        return render(request, self.template_name, context)


def price_history_chart_offers(request, offer_id):
    offer_queryset = Myoffers.objects.filter(offer_id=offer_id)
    if offer_queryset.exists():
        first_offer = offer_queryset.first()
        offer_url = first_offer.offer_url
        match = re.search(r'PLID(\d+)', offer_url)
        if match:
            plid = match.group(1)
    else:
        print(f'Offer with ID {offer_id} not found')

    product = get_object_or_404(Product, id=plid)
    price_history = product.pricehistory_set.all()
    aggregated_prices = price_history.annotate(month=TruncMonth('timestamp')).values('month').annotate(
        avg_price=Avg('price')).order_by('month')

    labels = [entry['month'].strftime('%m') for entry in aggregated_prices]
    prices = [round(entry['avg_price'], 2) if entry['avg_price'] is not None else None for entry in aggregated_prices]

    data = {
        'labels': labels,
        'prices': prices,
    }

    return JsonResponse(data)


class ExtractDayOfWeek:
    pass


def sales_by_week_chart(request, offer_id):
    user_id = request.user.id
    task_result = generate_sales_data.delay(offer_id, user_id)
    task_status = task_result.status
    task_result.wait()
    if task_result.successful():
        task_data = task_result.result
        return JsonResponse(task_data)
    else:
        return JsonResponse({'error': 'Failed to generate sales data'}, status=500)
