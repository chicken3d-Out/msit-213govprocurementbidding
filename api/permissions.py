from rest_framework.permissions import BasePermission


class IsAgencyOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        from rest_framework.permissions import SAFE_METHODS
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and (
            request.user.is_agency or request.user.is_staff
        )


class IsVerifiedVendor(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        vendor = getattr(request.user, 'vendor_profile', None)
        return vendor and vendor.is_verified
