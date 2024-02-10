from datetime import timedelta

from datetime import datetime

from django import forms
from django.utils import timezone
from django import template


class InvoiceForm(forms.Form):
    business_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Business name',
        }),
    )

    street = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Customer address',
        }),
    )

    tax_number = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tax number',
        }),
    )

    reg_number = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reg. number',
        }),
    )


class DateRangeService:
    @staticmethod
    def get_date_range(filter_param):
        current_date = timezone.now().date()
        very_early_date = datetime.min.date()

        date_ranges = {
            'today': (current_date, current_date),
            'this-week': (current_date - timedelta(days=current_date.weekday()), current_date),
            'this-month': (current_date.replace(day=1), current_date.replace(day=1) + timedelta(days=31)),
            'this-year': (current_date.replace(day=1), current_date.replace(day=1) + timedelta(days=365)),
            'last-7-days': (current_date - timedelta(days=7), current_date),
            'last-30-days': (current_date - timedelta(days=30), current_date),
            'last-90-days': (current_date - timedelta(days=90), current_date),
            'last-year': (current_date - timedelta(days=365), current_date),
            'all': (very_early_date, current_date),
        }
        return date_ranges.get(filter_param, (None, None))

    @staticmethod
    def is_all_time(filter_param):
        return filter_param == 'all'


def convert_to_db_format(date_string):
    date_format = '%b. %d, %Y, %I:%M %p'
    date_object = datetime.strptime(date_string, date_format)
    return date_object


register = template.Library()


@register.filter
def replace_spaces(value):
    return value.replace("-", " ")
