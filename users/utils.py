from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator as token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_verify_email(request, user):
    current_site = get_current_site(request)
    context = {
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "user": user,
        "token": token_generator.make_token(user),
        "domain": current_site.domain,
    }
    message = render_to_string('emails/verify_email.html', context=context)
    email = EmailMultiAlternatives("Welcome to TakeaBot: Your new world of marketplace analytics!", body=strip_tags(message), to=[user.email])
    email.attach_alternative(message, "text/html")
    email.send()


