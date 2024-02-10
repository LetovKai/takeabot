from django.urls import path
from . import views

app_name = 'myoffers'

urlpatterns = [
    path('', views.MyoffersListView.as_view(), name='myoffers'),

    path('toggle_autoprice/<int:sale_id>/', views.toggle_autoprice, name='toggle_autoprice'),
    path('edit_offer/', views.edit_offer, name='edit_offer'),
    path('update_offers/', views.upd_offers, name='update_offers'),
    path('upd_market_price/', views.upd_market_price, name='upd_market_price'),
    path('upd_one_market_price/<int:offer_id>/', views.upd_one_market_price, name='upd_one_market_price'),
    # path('get_offer_data/', views.get_offer_data, name='get_offer_data'),
    path('price_history_chart_offers/<int:offer_id>/', views.price_history_chart_offers, name='price_history_chart_offers'),
    path('sales_by_week_chart/<int:offer_id>/', views.sales_by_week_chart, name='sales_by_week_chart'),

]