from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from myoffers.update_myoffers import update_myoffers
from mysales.sales_update import full_update_sales, day_update_sales


@receiver(user_logged_in)
def user_registered(sender, request, user, **kwargs):
    api_key = user.api_key
    user_id = user.id
    update_myoffers(api_key, user_id)
    day_update_sales(api_key, user_id)
