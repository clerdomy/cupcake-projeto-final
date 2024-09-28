import requests


from django import forms
from core.models import Newsletter, Address, Contact, Profile
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

import PAIS


class AccountDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio']

class CustomPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']



class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'email', 'subject', 'message']

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['subject', 'message']


class AddressForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].choices = self.get_country_choices()

    def get_country_choices(self):
        # Fazendo uma requisição para a API REST Countries
        # response = requests.get("https://restcountries.com/v3.1/all")
        # if response.status_code == 200:
        #     countries = response.json()
        #     country_choices = [(country['name']['common'], country['name']['common']) for country in countries]
        #     country_choices.sort(key=lambda x: x[0])
        return PAIS.PAIS
        
        return [('Brazil', 'Brazil')]
    
    class Meta:
        model = Address
        fields = [
            'country', 'first_name', 'last_name', 'company_name', 'street_address',
            'apartment_suite', 'city', 'state', 'postcode', 'email', 'phone', 'order_notes'
        ]
        widgets = {
            'country': forms.Select(attrs={'class': 'myniceselect nice-select wide rounded-0'}),
            'first_name': forms.TextInput(attrs={'placeholder': ''}),
            'last_name': forms.TextInput(attrs={'placeholder': ''}),
            'company_name': forms.TextInput(attrs={'placeholder': ''}),
            'street_address': forms.TextInput(attrs={'placeholder': 'Street address'}),
            'apartment_suite': forms.TextInput(attrs={'placeholder': 'Apartment, suite, unit etc. (optional)'}),
            'city': forms.TextInput(attrs={'placeholder': ''}),
            'state': forms.TextInput(attrs={'placeholder': ''}),
            'postcode': forms.TextInput(attrs={'placeholder': ''}),
            'email': forms.EmailInput(attrs={'placeholder': ''}),
            'phone': forms.TextInput(attrs={'placeholder': ''}),
            'order_notes': forms.Textarea(attrs={
                'cols': 30, 'rows': 10, 'placeholder': 'Notes about your order, e.g. special notes for delivery.'
            }),
        }

