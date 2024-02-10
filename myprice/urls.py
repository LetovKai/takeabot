from django.urls import path
from . import views

urlpatterns = [
    path('', views.MyoffersListView.as_view(), name='myprice'),
]