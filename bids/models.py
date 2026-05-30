from django.db import models
from accounts.models import User, VendorProfile
from procurement.models import Procurement


class Bid(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        WITHDRAWN = 'WITHDRAWN', 'Withdrawn'
        WINNING   = 'WINNING',   'Winning'
        LOSING    = 'LOSING',    'Losing'

    procurement  = models.ForeignKey(Procurement, on_delete=models.PROTECT, related_name='bids')
    vendor       = models.ForeignKey(VendorProfile, on_delete=models.PROTECT, related_name='bids')
    amount       = models.DecimalField(max_digits=14, decimal_places=2)
    proposal     = models.FileField(upload_to='proposals/%Y/%m/')
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('procurement', 'vendor')

    def __str__(self):
        return f"Bid by {self.vendor} on {self.procurement.reference_no}"


class BidOpenEvent(models.Model):
    """NIST audit log: tracks exactly who opened a bid and when."""
    bid        = models.ForeignKey(Bid, on_delete=models.PROTECT, related_name='open_events')
    opened_by  = models.ForeignKey(User, on_delete=models.PROTECT)
    opened_at  = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ['-opened_at']

    def __str__(self):
        return f"{self.opened_by} opened bid#{self.bid_id} at {self.opened_at}"
