import logging
from django.contrib import admin
from .models import Procurement, AwardedContract

audit_log = logging.getLogger('audit')


@admin.register(Procurement)
class ProcurementAdmin(admin.ModelAdmin):
    list_display = ('reference_no', 'title', 'status', 'deadline', 'reveal_date', 'posted_by')
    list_filter = ('status',)
    search_fields = ('reference_no', 'title')
    readonly_fields = ('reference_no', 'created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        action = 'UPDATED' if change else 'CREATED'
        audit_log.info(
            f"ADMIN_PROCUREMENT_{action} | user={request.user.username} | ref={obj.reference_no}"
        )


@admin.register(AwardedContract)
class AwardedContractAdmin(admin.ModelAdmin):
    list_display = ('procurement', 'awarded_to', 'contract_value', 'awarded_at')
    readonly_fields = ('awarded_at',)
