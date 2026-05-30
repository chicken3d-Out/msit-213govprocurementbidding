from django import forms
from django.utils import timezone
from .models import Procurement, AwardedContract
from bids.models import Bid
import uuid


class ProcurementForm(forms.ModelForm):
    class Meta:
        model = Procurement
        fields = ['title', 'description', 'budget', 'deadline', 'reveal_date', 'status']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'reveal_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def clean(self):
        cleaned = super().clean()
        deadline = cleaned.get('deadline')
        reveal_date = cleaned.get('reveal_date')
        if deadline and reveal_date and reveal_date < deadline:
            raise forms.ValidationError('Reveal date must be on or after the deadline.')
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        if not obj.reference_no:
            year = timezone.now().year
            short = str(uuid.uuid4()).split('-')[0].upper()
            obj.reference_no = f"GOV-{year}-{short}"
        if commit:
            obj.save()
        return obj


class AwardContractForm(forms.ModelForm):
    class Meta:
        model = AwardedContract
        fields = ['awarded_to', 'contract_value', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, procurement=None, **kwargs):
        super().__init__(*args, **kwargs)
        if procurement:
            vendor_ids = Bid.objects.filter(
                procurement=procurement, status='SUBMITTED'
            ).values_list('vendor_id', flat=True)
            from accounts.models import VendorProfile
            self.fields['awarded_to'].queryset = VendorProfile.objects.filter(id__in=vendor_ids)
