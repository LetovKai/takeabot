from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    name = forms.CharField(label='name',
                               widget=forms.TextInput(attrs={
                                   'class': 'form-control',
                                   'placeholder': 'Your Name',
                               }),
                               )
    email = forms.EmailField(label='name',
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                               'placeholder': 'Your E-mail',
                           }),
                           )
    subject = forms.CharField(label='name',
                           widget=forms.TextInput(attrs={
                               'class': 'form-control',
                               'placeholder': 'Please specify your subject',
                           }),
                           )
    message = forms.CharField(label='name',
                           widget=forms.Textarea(attrs={
                               'class': 'form-control',
                               'placeholder': 'Please provide your message',
                               'rows': 5,
                           }),
                           )
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
