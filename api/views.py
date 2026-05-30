from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from procurement.models import Procurement, AwardedContract
from .serializers import AwardedContractSerializer, ProcurementPublicSerializer


class AwardedContractListView(generics.ListAPIView):
    """
    Public endpoint for transparency portals.
    Returns awarded contracts with losing bidder info masked.
    """
    serializer_class = AwardedContractSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['procurement__reference_no', 'procurement__title']
    ordering_fields = ['awarded_at', 'contract_value']
    ordering = ['-awarded_at']

    def get_queryset(self):
        return AwardedContract.objects.select_related(
            'procurement', 'awarded_to'
        ).all()


class AwardedContractDetailView(generics.RetrieveAPIView):
    serializer_class = AwardedContractSerializer
    permission_classes = [AllowAny]
    queryset = AwardedContract.objects.select_related('procurement', 'awarded_to')


class ProcurementPublicListView(generics.ListAPIView):
    serializer_class = ProcurementPublicSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['reference_no', 'title']
    ordering_fields = ['created_at', 'deadline', 'budget']
    ordering = ['-created_at']

    def get_queryset(self):
        return Procurement.objects.exclude(status__in=['DRAFT', 'CANCELLED'])
