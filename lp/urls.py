from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.ContactView.as_view(), name='index'),
    path('contact_form/', views.contact_form, name='contact_form'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms, name='terms'),
    path('inner/', views.inner, name='inner'),
]