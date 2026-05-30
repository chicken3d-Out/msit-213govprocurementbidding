from django.db import models
from django.utils import timezone
from accounts.models import User


class Procurement(models.Model):
    class Status(models.TextChoices):
        DRAFT     = 'DRAFT',     'Draft'
        OPEN      = 'OPEN',      'Open for bidding'
        CLOSED    = 'CLOSED',    'Bidding closed'
        AWARDED   = 'AWARDED',   'Contract awarded'
        CANCELLED = 'CANCELLED', 'Cancelled'

    posted_by    = models.ForeignKey(User, on_delete=models.PROTECT, related_name='postings')
    title        = models.CharField(max_length=300)
    description  = models.TextField()
    budget       = models.DecimalField(max_digits=14, decimal_places=2)
    deadline     = models.DateTimeField(help_text='When bidding closes')
    reveal_date  = models.DateTimeField(help_text='When bid contents become visible (blind until then)')
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    reference_no = models.CharField(max_length=50, unique=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def is_blind(self):
        return timezone.now() < self.reveal_date

    def is_accepting_bids(self):
        return self.status == self.Status.OPEN and timezone.now() < self.deadline

    def __str__(self):
        return f"{self.reference_no} – {self.title}"


class AwardedContract(models.Model):
    procurement    = models.OneToOneField(Procurement, on_delete=models.PROTECT, related_name='contract')
    awarded_to     = models.ForeignKey('accounts.VendorProfile', on_delete=models.PROTECT)
    awarded_by     = models.ForeignKey(User, on_delete=models.PROTECT)
    awarded_at     = models.DateTimeField(auto_now_add=True)
    contract_value = models.DecimalField(max_digits=14, decimal_places=2)
    notes          = models.TextField(blank=True)

    def __str__(self):
        return f"Contract: {self.procurement.reference_no} → {self.awarded_to}"
