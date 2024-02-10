from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from myoffers.update_myoffers import update_myoffers
from django.views.generic.list import ListView
from myoffers.models import Myoffers
from django.shortcuts import redirect


class MyoffersListView(LoginRequiredMixin, ListView):
    model = Myoffers
    template_name = 'myprice/myprice.html'
    context_object_name = 'myoffers'
    paginate_by = 100

    def get(self, request, *args, **kwargs):
        api_key = request.user.api_key
        user_id = request.user.id
        response_status_code = update_myoffers(api_key, user_id)
        if response_status_code == 401:
            return redirect('users:profile')

        return super().get(request, *args, **kwargs)


class OffersView(LoginRequiredMixin, View):
    template_name = 'myprice/myprice.html'

    def get(self, request, *args, **kwargs):
        api_key = request.user.api_key
        user_id = request.user.id

        response_status_code = update_myoffers(api_key, user_id)
        if response_status_code == 401:
            return redirect('users:profile')
        offers = Myoffers.objects.all()
        context = {
            'offers': offers,
        }
        return render(request, self.template_name, context)


def myprice(request):
    pass
