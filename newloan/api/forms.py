from django import forms
from api.models import Investor

class InvestorProfileForm(forms.ModelForm):
    class Meta:
        model = Investor
        fields = ['phone_number']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
        } 