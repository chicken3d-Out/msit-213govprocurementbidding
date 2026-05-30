from rest_framework import serializers
from procurement.models import Procurement, AwardedContract
from bids.models import Bid


class AwardedContractSerializer(serializers.ModelSerializer):
    procurement_reference = serializers.CharField(source='procurement.reference_no', read_only=True)
    procurement_title = serializers.CharField(source='procurement.title', read_only=True)
    awarded_to_company = serializers.CharField(source='awarded_to.company_name', read_only=True)
    # Mask losing bidder info — only winner company name is exposed
    losing_bid_count = serializers.SerializerMethodField()

    class Meta:
        model = AwardedContract
        fields = [
            'id', 'procurement_reference', 'procurement_title',
            'awarded_to_company', 'contract_value', 'awarded_at',
            'losing_bid_count', 'notes',
        ]

    def get_losing_bid_count(self, obj):
        return Bid.objects.filter(
            procurement=obj.procurement, status='LOSING'
        ).count()


class ProcurementPublicSerializer(serializers.ModelSerializer):
    is_blind = serializers.SerializerMethodField()
    bid_count = serializers.SerializerMethodField()

    class Meta:
        model = Procurement
        fields = [
            'id', 'reference_no', 'title', 'description',
            'budget', 'deadline', 'reveal_date', 'status',
            'is_blind', 'bid_count', 'created_at',
        ]

    def get_is_blind(self, obj):
        return obj.is_blind()

    def get_bid_count(self, obj):
        if obj.is_blind():
            return None  # masked while blind
        return obj.bids.filter(status='SUBMITTED').count()
