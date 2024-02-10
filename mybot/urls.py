from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='mybot'),

    path('run_script/', views.run_script, name='run_script'),
    path('parse_serval/', views.parse_serval, name='parse_serval'),
    path('price_history_chart/<int:product_id>/', views.price_history_chart, name='price_history_chart')
]