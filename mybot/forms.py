from django import forms
import django_filters
from django.db.models import Q
from django.forms import CheckboxInput
from django_filters import RangeFilter
from django_filters.widgets import RangeWidget

from .models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.ChoiceFilter(label='Category', choices=[])
    price = RangeFilter(label='Price', widget=RangeWidget(attrs={'class': 'form-control'}))
    review = RangeFilter(label='Review', widget=RangeWidget(attrs={'class': 'form-control'}))
    none_brand = django_filters.BooleanFilter(
        method='filter_none_brand',
        label='Only None Brand',
        widget=CheckboxInput(attrs={'class': 'form-check-input me-1', 'aria-label': '...'})
    )

    search = django_filters.CharFilter(
        method='filter_search',
        label='Search',
        widget=forms.TextInput(attrs={'placeholder': 'Search by Name, Tsin, Brand'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['category'].extra['choices'] = [
            (category, category) for category in Product.objects.values_list('category', flat=True).distinct().order_by('category')
        ]

    class Meta:
        model = Product
        fields = ['category', 'price', 'review', 'search']

    def filter_none_brand(self, queryset, name, value):
        if value:
            return queryset.filter(brand='None brand')
        return queryset

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(id__icontains=value) |
            Q(tsin__icontains=value) |
            Q(name__icontains=value) |
            Q(brand__icontains=value)
        )
