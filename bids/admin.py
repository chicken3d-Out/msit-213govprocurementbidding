import logging
from django.contrib import admin
from .models import Bid, BidOpenEvent

audit_log = logging.getLogger('audit')


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('procurement', 'vendor', 'amount', 'status', 'submitted_at')
    list_filter = ('status',)
    readonly_fields = ('submitted_at', 'updated_at')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('procurement', 'vendor')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        audit_log.info(
            f"ADMIN_BID_EDIT | user={request.user.username} | bid_id={obj.pk} "
            f"| ref={obj.procurement.reference_no}"
        )


@admin.register(BidOpenEvent)
class BidOpenEventAdmin(admin.ModelAdmin):
    list_display = ('bid', 'opened_by', 'opened_at', 'ip_address')
    readonly_fields = ('bid', 'opened_by', 'opened_at', 'ip_address', 'user_agent')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
