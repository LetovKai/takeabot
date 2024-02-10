from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Avg, Q
from django.db.models.functions import TruncMonth

from . import parser
from .models import Product
from django.views.generic.list import ListView
from .forms import ProductFilter
from .serval import parse_chart_data
from django.shortcuts import render
from django.http import JsonResponse
from .models import PriceHistory


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'mybot/mybot.html'
    context_object_name = 'products'
    paginate_by = 16

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = ProductFilter(self.request.GET, queryset=queryset)
        queryset = self.filterset.qs

        search_query = self.request.GET.get('query', '')
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query) | Q(brand__icontains=search_query))

        return queryset

    def get_context_data(self, **kwargs): #filters
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            self.object_list = self.get_queryset()
            page = request.GET.get('page', 1)
            paginator = Paginator(self.object_list, 16)
            try:
                products = paginator.page(page)
            except PageNotAnInteger:
                products = paginator.page(1)
            except EmptyPage:
                products = paginator.page(paginator.num_pages)

            products_data = []
            for product in products:
                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'img': product.img,
                    'url': product.url,
                    'brand': product.brand,
                    'brand_url': product.brand_url,
                    'review': product.review,
                    'rating': product.rating,
                    'price': product.price,
                }
                products_data.append(product_data)
            return JsonResponse({'products': products_data, 'has_next': products.has_next()}, safe=False)

        return super().get(request, *args, **kwargs)


def price_history_chart(request, product_id):
    price_history = PriceHistory.objects.filter(product_id=product_id)
    aggregated_prices = price_history.annotate(month=TruncMonth('timestamp')).values('month').annotate(
        avg_price=Avg('price')).order_by('month')

    labels = [entry['month'].strftime('%Y-%m') for entry in aggregated_prices]
    prices = [round(entry['avg_price'], 2) if entry['avg_price'] is not None else None for entry in aggregated_prices]

    data = {
        'labels': labels,
        'prices': prices,
    }

    return JsonResponse(data)


@login_required
def run_script(request):
    if request.method == 'POST':
        parser.parse_all.delay()
        return render(request, 'core/blank.html')


@login_required
def parse_serval(request):
    if request.method == 'POST':
        parse_chart_data.delay()
        return render(request, 'core/blank.html')
