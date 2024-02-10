from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views import View
from .forms import ContactForm
from django.core.mail import send_mail, EmailMultiAlternatives
from django.http import JsonResponse


def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            send_mail(
                subject,
                f'From: {name}\nEmail: {email}\n{subject}\n\n{message}',
                'info@takeabot.co.za',  # info email
                ['Kai.letov.k@proton.me', 'support@takeabot.co.za'],  # support email
                fail_silently=False,
            )
            message = render_to_string('emails/contact_form.html')
            emailing = EmailMultiAlternatives("TakeaBot request confirmation: We have received your message",
                                           body=strip_tags(message), to=[email])
            emailing.attach_alternative(message, "text/html")
            emailing.send()
            form.save()
            # return redirect('index')
            return render(request, 'partials/contact_form.html', {'form': form})
        else:
            return render(request, 'partials/contact_form.html', {'form': form})


class ContactView(View):
    def get(self, request):
        form = ContactForm()
        return render(request, 'lp/index.html', {'form': form})



def inner(request):
    return render(request, 'lp/inner-page.html')

def privacy_policy(request):
    return render(request, 'lp/privacy_policy.html')

def terms(request):
    return render(request, 'lp/terms.html')