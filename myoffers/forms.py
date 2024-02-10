from django import forms
from myoffers.models import Myoffers


class CostPriceForm(forms.ModelForm):
    cost_price = forms.CharField(widget=forms.TextInput(attrs={
                                     'class': 'form-control col-md-12',
                                     'placeholder': 'selfcost',
                                 }),
                                 )

    class Meta:
        model = Myoffers
        fields = ['cost_price']
