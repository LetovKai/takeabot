from celery import shared_task
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordContextMixin, UserModel
from django.core.exceptions import ValidationError

from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, UpdateView, FormView, TemplateView

from myoffers.update_myoffers import update_myoffers
from mysales.sales_update import full_update_sales
from takeabot import settings
from users.forms import LoginUserForm, RegisterUserForm, ProfileUserForm, UserPasswordChangeForm, \
    PasswordResetConfirmForm
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse_lazy
from .forms import ProfileUserForm, UserPasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import User
from .payments import payments_first, payments_last
from .utils import send_verify_email
from django.contrib.auth.tokens import default_token_generator as token_generator


class EmailVerify(View):
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        if user is not None and token_generator.check_token(user, token):
            user.email_verify = True
            user.save()
            login(request, user)
            api_key = user.api_key
            user_id = user.id
            update_myoffers(api_key, user_id)
            full_update_sales(api_key, user_id)
            return redirect('dashboard')
        return redirect('users:invalid_verification')

    @staticmethod
    def get_user(uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (
                TypeError,
                ValueError,
                OverflowError,
                User.DoesNotExist,
                ValidationError,
        ):
            user = None
        return user


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {
        'title': 'Login'
    }
    success_url = reverse_lazy('dashboard')


class RegisterUser(View):
    template_name = 'users/register.html'

    def get(self, request):
        context = {
            'form': RegisterUserForm()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            send_verify_email(request, user)
            api_key = user.api_key
            user_id = user.id
            full_update.delay(api_key, user_id)
            return redirect('users:confirm_email')

        context = {
            'form': form
        }
        return render(request, self.template_name, context)


class ProfileUser(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    form_class = ProfileUserForm
    template_name = 'users/profile.html'
    extra_context = {
        'title': 'Profile',
        'default_image': settings.DEFAULT_USER_IMAGE,
    }
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = self.request.user
        uploaded_photo = self.request.FILES.get('photo')
        if uploaded_photo:
            user.photo = uploaded_photo
            user.save()

        return super().form_valid(form)


class UserPasswordChange(LoginRequiredMixin, PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:profile")
    template_name = "users/password-change-form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Password successfully changed.")
        return response


class PasswordResetConfirmView(PasswordContextMixin, FormView):
    form_class = PasswordResetConfirmForm
    template_name = 'users/password_reset_confirm.html',
    success_url = reverse_lazy('users:password_reset_complete')


class BillingInfoView(TemplateView):
    template_name = 'users/billing.html'

    def get_context_data(self, **kwargs):
        check_id, data = payments_first()

        context = super().get_context_data(**kwargs)
        context['check_id'] = check_id

        return context

    # return render(request, self.template_name, context)


def payments_check(request):
    check_id = request.GET.get('id', None)
    print(check_id)
    checkout = payments_last(check_id)
    print(checkout)

    return render(request, 'core/payments_check.html')


@shared_task
def full_update(api_key, user_id):
    update_myoffers(api_key, user_id)
    full_update_sales(api_key, user_id)
