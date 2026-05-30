from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from .forms import VendorRegistrationForm, AgencyRegistrationForm


def register_vendor(request):
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('procurement:list')
    else:
        form = VendorRegistrationForm()
    return render(request, 'accounts/register_vendor.html', {'form': form})


def register_agency(request):
    if request.method == 'POST':
        form = AgencyRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('procurement:list')
    else:
        form = AgencyRegistrationForm()
    return render(request, 'accounts/register_agency.html', {'form': form})
