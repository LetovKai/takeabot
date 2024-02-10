from django.contrib.auth.views import LogoutView, PasswordChangeView, PasswordChangeDoneView, PasswordResetView, \
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView

from . import views
from .forms import PasswordResetConfirmForm
from .views import BillingInfoView

app_name = 'users'

urlpatterns = [
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password-change/', views.UserPasswordChange.as_view(), name='password_change'),
    path('password-change/done/', PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),

    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset_form.html',
                                                      email_template_name='users/password_reset_email.html',
                                                      html_email_template_name='users/password_reset_email.html',
                                                      success_url=reverse_lazy('users:password_reset_done')),
         name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html',
                                          form_class=PasswordResetConfirmForm,
                                          success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    path('register/', views.RegisterUser.as_view(), name='register'),
    path('profile/', views.ProfileUser.as_view(), name='profile'),

    path('confirm_email/', TemplateView.as_view(template_name='users/confirmation_email.html'), name='confirm_email'),
    path('verify-email/<uidb64>/<token>/', views.EmailVerify.as_view(), name='verify_email'),
    path('invalid_verification/', TemplateView.as_view(template_name='users/invalid_verification.html'),
         name='invalid_verification'),

    path('billing/', BillingInfoView.as_view(), name='billing'),

    # path('payments/', views.payments, name='payments'),
    path('payments_check/', views.payments_check, name='payments_check'),
]
