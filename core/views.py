from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin

from mysales.forms import replace_spaces
from django.views import View
from django.shortcuts import render
from mysales.models import Mysales


def index(request):
    return render(request, 'core/blank.html')


def pages_error_404(request, exception):
    return render(request, 'core/pages-error-404.html')


class MainView(LoginRequiredMixin, View):
    template_name = 'core/dashboard.html'

    def get(self, request, *args, **kwargs):
        api_key = request.user.api_key
        user_id = request.user.id

        checkboxes = {
            'cpt': request.GET.get('cpt', False) == 'on',
            'jhb': request.GET.get('jhb', False) == 'on',
            'returned': request.GET.get('ret', False) == 'on',
            'cancelations': request.GET.get('canc', False) == 'on',
        }
        global_filter = request.GET.get('global_filter')
        start_date_str = request.GET.get('start_date', '')
        end_date_str = request.GET.get('end_date', '')

        formatted_start_date = datetime.strptime(start_date_str, "%Y-%m-%d") if start_date_str else None
        formatted_end_date = datetime.strptime(end_date_str, "%Y-%m-%d") if end_date_str else None
        start_date = formatted_start_date.strftime("%Y-%m-%d") if formatted_start_date else None
        end_date = formatted_end_date.strftime("%Y-%m-%d") if formatted_end_date else None

        if global_filter is not None:
            sale_filter = request.GET.get('global_filter')
            ret_filter = request.GET.get('global_filter')
            can_filter = request.GET.get('global_filter')
            chart_filter = request.GET.get('global_filter')
            rec_filter = request.GET.get('global_filter')
            top_filter = request.GET.get('global_filter')
        else:
            sale_filter = request.GET.get('sale_filter', 'today')
            ret_filter = request.GET.get('ret_filter', 'all')
            can_filter = request.GET.get('can_filter', 'all')
            chart_filter = request.GET.get('chart_filter', 'all')
            rec_filter = request.GET.get('rec_filter', 'all')
            top_filter = request.GET.get('top_filter', 'all')

        sales_data = Mysales.get_sales(sale_filter, user_id, start_date, end_date)
        returns_data = Mysales.get_returns(ret_filter, user_id, start_date, end_date)
        can_data = Mysales.get_cancelations(can_filter, user_id, start_date, end_date)
        chart_sales_dates, chart_sales_values = Mysales.get_chart_data(chart_filter, user_id, start_date, end_date)
        recent_sales, total_pure_profit, total_fee, total_cost_price, all_cost_prices, cost_price_percentage, fee_percentage, pure_profit_percentage = Mysales.recent_sales(rec_filter, user_id, checkboxes, start_date, end_date)
        top_sales = Mysales.top_sales(top_filter, api_key, user_id)

        sales_percentage = 0
        return_percentage = 0
        cancelations_percentage = 0

        if global_filter is not None:
            sales_total = sales_data['sales_total']
            return_total = returns_data['return_total']
            cancelations_total = can_data['cancelations_total']

            total_sum = sales_total + return_total + cancelations_total
            sales_percentage = round((sales_total / total_sum) * 100, 2) if total_sum != 0 else 0
            return_percentage = round((return_total / total_sum) * 100, 2) if total_sum != 0 else 0
            cancelations_percentage = round((cancelations_total / total_sum) * 100, 2) if total_sum != 0 else 0

        danger_statuses = [
            'Cancelled by Customer', 'Cancelled by Takealot',
            'Cancelled by Takealot - DC Stock Inquiry', 'Cancelled - Late Delivery',
            'Returned', 'Cancelled by Customer', 'Cancelled - Inbound Exception',
        ]

        warning_statuses = ["Inter DC Transfer", "Preparing for Customer"]

        sale_filter_label = replace_spaces(sale_filter).capitalize()
        ret_filter_label = replace_spaces(ret_filter).capitalize()
        can_filter_label = replace_spaces(can_filter).capitalize()
        chart_filter_label = replace_spaces(chart_filter).capitalize()
        rec_filter_label = replace_spaces(rec_filter).capitalize()
        top_filter_label = replace_spaces(top_filter).capitalize()

        context = {
            'sale_filter_label': sale_filter_label,
            'ret_filter_label': ret_filter_label,
            'can_filter_label': can_filter_label,
            'chart_filter_label': chart_filter_label,
            'rec_filter_label': rec_filter_label,
            'top_filter_label': top_filter_label,
            'chart_sales_dates': chart_sales_dates,
            'chart_sales_values': chart_sales_values,
            'recent_sales': recent_sales,
            'warning_statuses': warning_statuses,
            'danger_statuses': danger_statuses,
            'top_sales': top_sales,
            'total_fee': total_fee,
            'total_pure_profit': total_pure_profit,
            'total_cost_price': total_cost_price,
            'all_cost_prices': all_cost_prices,
            'sales_percentage': sales_percentage,
            'return_percentage': return_percentage,
            'cancelations_percentage': cancelations_percentage,
            'pure_profit_percentage': pure_profit_percentage,
            'fee_percentage': fee_percentage,
            'cost_price_percentage': cost_price_percentage,
            **sales_data,
            **returns_data,
            **can_data,
        }

        return render(request, self.template_name, context)
