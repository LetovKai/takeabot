from django import forms
from django.contrib.auth import get_user_model, password_validation, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from users.utils import send_verify_email


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Username',
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Enter your username',
                               }),
                               )

    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Enter your password',
                               }),
                               )

    remember = forms.BooleanField(
        label='Remember me',
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'password', 'remember']

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )

            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                # Проверка наличия атрибута email_verify у user_cache
                if not getattr(self.user_cache, 'email_verify', False):
                    send_verify_email(self.request, self.user_cache)
                    raise ValidationError(
                        "Email not verify, check your email",
                        code="invalid_login",
                        params={"username": self.username_field.verbose_name},
                    )

                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Username',
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Enter your username',
                               }),

                               )
    password1 = forms.CharField(label='Password',
                                widget=forms.PasswordInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Enter your password',
                                }),

                                )
    password2 = forms.CharField(label='Confirm Password',
                                widget=forms.PasswordInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Confirm your password',
                                }),

                                )
    api_key = forms.CharField(label='Takealot Api Key',
                              widget=forms.PasswordInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Enter your takealot api key',
                              }),

                              )
    terms_and_policy = forms.BooleanField(
        initial=False,
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        }),
    )

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2', 'api_key', 'terms_and_policy']
        labels = {
            'email': "E-mail",
            'first_name': "First name",
            'last_name': "Last name",
        }
        widgets = {
            'email': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your E-mail',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Last name',
            }),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Email address already exists')
        return email


class ProfileUserForm(forms.ModelForm):
    # username = forms.CharField(label='Username',
    #                            disabled=True,
    #                            widget=forms.TextInput(attrs={
    #                                'class': 'form-control',
    #                                'placeholder': 'Enter your username',
    #                            }),
    #                            )
    # email = forms.CharField(label='E-mail',
    #                         disabled=True,
    #                         widget=forms.TextInput(attrs={
    #                             'class': 'form-control',
    #                             'placeholder': 'Enter your E-mail',
    #                         }),
    #                         )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'phone', 'sellers_id', 'api_key', 'company_name', 'street', 'city', 'postal_code',
                  'photo', ]
        labels = {
            'first_name': "First name",
            'last_name': "Last name",
            'sellers_id': "Sellers ID",
            'company_name': "Company name",
            'street': "Company address",
            'city': "Company City",
            'postal_code': "Company postal code",
        }
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your First name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your Last name',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your phone number',
            }),
            'api_key': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your takealot ApiKey',
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your company name',
            }),
            'street': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your company address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your city',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your postal code',
            }),
            'sellers_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your sellers ID',
            }),
        }


class PasswordResetConfirmForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'}),
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password again"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password again'}),
    )


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Current Password',
                                   widget=forms.PasswordInput(attrs={
                                       'class': 'form-control',
                                       'placeholder': 'Enter your current password',
                                   }),
                                   )
    new_password1 = forms.CharField(label='New Password',
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control',
                                        'placeholder': 'Enter your new password',
                                    }),
                                    )
    new_password2 = forms.CharField(label='Re-enter New Password',
                                    widget=forms.PasswordInput(attrs={
                                        'class': 'form-control',
                                        'placeholder': 'Re-enter your new password',
                                    }),
                                    )
