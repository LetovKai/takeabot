from django.urls import path
from . import views

app_name = 'mysales'

urlpatterns = [
    path('', views.CalculateSalesView.as_view(), name='mysales'),
    path('update_sales/', views.upd_sales, name='update_sales'),
    path('generate_invoice/<int:order_item_id>/', views.GenerateInvoiceView.as_view(), name='generate_invoice'),

    # path('update_cost_price/<int:myoffer_id>/', views.update_cost_price, name='update_cost_price'),
]
