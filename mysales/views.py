from django.contrib.auth.mixins import LoginRequiredMixin
from myoffers.update_myoffers import update_myoffers
from myoffers.forms import CostPriceForm
from .sales_update import day_update_sales, full_update_sales, month_update_sales
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.dateparse import parse_date
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from myoffers.models import Myoffers
from .forms import replace_spaces, InvoiceForm
from .models import Mysales


class GenerateInvoiceView(View):

    def post(self, request, order_item_id):
        business_name = request.POST.get('business_name', '')
        street = request.POST.get('street', '')
        tax_number = request.POST.get('tax_number', '')
        reg_number = request.POST.get('reg_number', '')
        required_tokens = 1
        mysales = get_object_or_404(Mysales, order_item_id=order_item_id, user_id=request.user.id)
        if not request.user.status:
            if request.user.invoice < required_tokens:
                return JsonResponse({'error': f"Oops! It looks like you`ve hit your monthly free invoice limit. Upgrade to premium now for unlimited invoicing."}, status=400)
        user = mysales.user
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{order_item_id}.pdf"'

        p = self.generate_invoice_pdf(response)
        p.build(self.get_invoice_content(mysales, user, street, tax_number, reg_number, business_name))
        request.user.invoice -= required_tokens
        request.user.save()
        return response

    def generate_invoice_pdf(self, response):
        p = SimpleDocTemplate(response, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
        return p

    def get_invoice_content(self, mysales, user, street, tax_number, reg_number, business_name):
        styles = getSampleStyleSheet()

        body_text_style = ParagraphStyle(
            'BodyText',
            parent=styles['BodyText'],
            fontSize=10,
        )

        right_aligned_style = ParagraphStyle(
            'RightAligned',
            parent=styles['BodyText'],
            alignment=2
        )

        heading_style = styles['Heading1']
        heading_style.alignment = 2

        content = []
        content.extend([
            Spacer(1, 12),
            Paragraph(f'<strong>Invoice #{mysales.order_id}</strong>', heading_style),
            Spacer(1, 12),
            Paragraph(f'<strong>Order date:</strong> {mysales.order_date.date()}', right_aligned_style),
            Paragraph(f'<strong>Invoice date:</strong> {mysales.order_date.date()}', right_aligned_style),
            Spacer(1, 12),
            Spacer(1, 12),
        ])
        if business_name != '':
            table_data = [
                [Paragraph(f'<strong>Invoice for</strong>', body_text_style),
                 Paragraph(f'<strong>Invoice issued by</strong>', body_text_style)],
                [Paragraph(f'<strong>Business name:</strong> {business_name}', body_text_style),
                 Paragraph(f'<strong>Merchant:</strong> {user.company_name}', body_text_style)],
                [Paragraph(f'<strong>Address:</strong> {street}', body_text_style),
                 Paragraph(f'<strong>Address:</strong> {user.street}, {user.city}, {user.postal_code}', body_text_style)],
                [Paragraph(f'<strong>TAX number:</strong> {tax_number}', body_text_style)],
                [Paragraph(f'<strong>Reg. number:</strong> {reg_number}', body_text_style)],
            ]
        else:
            table_data = [
                [Paragraph(f'<strong>Invoice for</strong>', body_text_style),
                 Paragraph(f'<strong>Invoice issued by</strong>', body_text_style)],
                [Paragraph(f'<strong>Customer:</strong> {mysales.customer}', body_text_style),
                 Paragraph(f'<strong>Merchant:</strong> {user.company_name}', body_text_style)],
                [Paragraph(f'<strong>Address:</strong> {street}', body_text_style),
                 Paragraph(f'<strong>Address:</strong> {user.street}, {user.city}, {user.postal_code}',
                           body_text_style)],
                [Paragraph(f'<strong>TAX number:</strong> {tax_number}', body_text_style)],
                [Paragraph(f'<strong>Reg. number:</strong> {reg_number}', body_text_style)],
            ]

        table_data_2 = [
            ['Description', 'Quantity', 'Price', 'Total'],
            [Paragraph(mysales.product_title, body_text_style), mysales.quantity, f"R {mysales.selling_price/mysales.quantity}",
             f"R {mysales.selling_price}"],
        ]

        table_style_2 = TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
        ])
        for _ in range(5):
            table_data_2.append(['', '', '', ''])

        table_2 = Table(table_data_2, style=table_style_2, colWidths=[290, 60, 100, 100])
        table = Table(table_data, colWidths=[350, 150])

        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))

        content.append(table)
        content.extend([
            Spacer(1, 12),
            HRFlowable(width="100%", thickness=1, color=colors.whitesmoke),
            Spacer(1, 12),
        ])
        content.append(table_2)

        total = mysales.selling_price
        content.extend([
            Spacer(1, 12),
            Paragraph(f'<strong>Total:</strong> R {total}', right_aligned_style),
        ])

        return content


class CalculateSalesView(LoginRequiredMixin, View):
    template_name = 'mysales/mysales.html'

    def process_checkbox(self, request, checkbox_name):
        return request.GET.get(checkbox_name, False) == 'on'

    def get_date_from_request(self, request, param_name):
        date_str = request.GET.get(param_name, '')
        return parse_date(date_str).strftime("%Y-%m-%d") if date_str else None

    def get_combined_context(self, request, user_id):
        rec_filter = request.GET.get('rec_filter', 'all')
        start_date = self.get_date_from_request(request, 'start_date')
        end_date = self.get_date_from_request(request, 'end_date')

        checkboxes = {
            'cpt': self.process_checkbox(request, 'cpt'),
            'jhb': self.process_checkbox(request, 'jhb'),
            'returned': self.process_checkbox(request, 'ret'),
            'cancelations': self.process_checkbox(request, 'canc'),
        }

        rec_filter_label = replace_spaces(rec_filter).capitalize()
        recent_sales, total_pure_profit, total_fee, total_cost_price, all_cost_prices, cost_price_percentage, fee_percentage, pure_profit_percentage = Mysales.recent_sales(
            rec_filter, user_id, checkboxes, start_date, end_date)
        cost_price_form = CostPriceForm()
        danger_statuses = ["Cancelled by Customer", "Cancelled - Late Delivery", "Cancelled by Takealot",
                           "Cancelled by Takealot - DC Stock Inquiry",
                           "Returned"]
        invoice_form = InvoiceForm()

        context = {
            'recent_sales': recent_sales,
            'total_pure_profit': total_pure_profit,
            'total_fee': total_fee,
            'total_cost_price': total_cost_price,
            'cost_price_form': cost_price_form,
            'danger_statuses': danger_statuses,
            'rec_filter_label': rec_filter_label,
            'checkboxes': checkboxes,
            'cpt_checked': checkboxes['cpt'],
            'jhb_checked': checkboxes['jhb'],
            'ret_checked': checkboxes['returned'],
            'canc_checked': checkboxes['cancelations'],
            'rec_filter': rec_filter,
            'invoice_form': invoice_form,
        }

        return context

    def get(self, request, *args, **kwargs):
        user_id = request.user.id
        context = self.get_combined_context(request, user_id)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user_id = request.user.id
        form = CostPriceForm(request.POST, instance=get_object_or_404(Myoffers, id=request.POST.get('offer_id')))
        print(form)
        if form.is_valid():
            print('ss')
            form.save()

        context = self.get_combined_context(request, user_id)
        context.update({'form': form})
        return render(request, self.template_name, context)


def upd_sales(request):
    api_key = request.user.api_key
    user_id = request.user.id
    update_myoffers(api_key, user_id)
    full_update_sales(api_key, user_id)
    redirect_url = request.META.get('HTTP_REFERER', reverse_lazy('mysales:mysales'))
    response = JsonResponse({'status': 'success'})
    response['HX-Redirect'] = redirect_url
    return response
