from django.urls import path
from . import consumers
from .views import MainView

websocket_urlpatterns = [
    path('ws/chat/', consumers.ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('', MainView.as_view(), name='dashboard'),
]

urlpatterns += websocket_urlpatterns
