from django import forms
from .models import Bid


class BidSubmitForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount', 'proposal']

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Bid amount must be positive.')
        return amount
