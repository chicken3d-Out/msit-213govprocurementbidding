from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, VendorProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_vendor', 'is_agency', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('is_vendor', 'is_agency')}),
    )


@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'registration_number', 'is_verified', 'verified_at')
    list_filter = ('is_verified',)
    actions = ['verify_vendors']

    def verify_vendors(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, verified_at=timezone.now())
    verify_vendors.short_description = 'Mark selected vendors as verified'
