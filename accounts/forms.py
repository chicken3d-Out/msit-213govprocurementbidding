from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, VendorProfile


class VendorRegistrationForm(UserCreationForm):
    company_name = forms.CharField(max_length=255)
    registration_number = forms.CharField(max_length=100)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_vendor = True
        if commit:
            user.save()
            VendorProfile.objects.create(
                user=user,
                company_name=self.cleaned_data['company_name'],
                registration_number=self.cleaned_data['registration_number'],
            )
        return user


class AgencyRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_agency = True
        if commit:
            user.save()
        return user
