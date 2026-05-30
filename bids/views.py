import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from procurement.models import Procurement
from .models import Bid, BidOpenEvent
from .forms import BidSubmitForm

audit_log = logging.getLogger('audit')


def _get_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


@login_required
def submit_bid(request, procurement_pk):
    proc = get_object_or_404(Procurement, pk=procurement_pk)

    if not request.user.is_vendor:
        messages.error(request, 'Only verified vendors can submit bids.')
        return redirect('procurement:detail', pk=procurement_pk)

    vendor = getattr(request.user, 'vendor_profile', None)
    if not vendor or not vendor.is_verified:
        messages.error(request, 'Your vendor account must be verified before bidding.')
        return redirect('procurement:detail', pk=procurement_pk)

    if not proc.is_accepting_bids():
        messages.error(request, 'This procurement is not currently accepting bids.')
        return redirect('procurement:detail', pk=procurement_pk)

    existing = Bid.objects.filter(procurement=proc, vendor=vendor).first()
    if existing:
        messages.warning(request, 'You have already submitted a bid for this procurement.')
        return redirect('procurement:detail', pk=procurement_pk)

    if request.method == 'POST':
        form = BidSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            bid = form.save(commit=False)
            bid.procurement = proc
            bid.vendor = vendor
            bid.save()

            ip = _get_ip(request)
            audit_log.info(
                f"BID_SUBMITTED | user={request.user.username} | vendor={vendor.company_name} "
                f"| ref={proc.reference_no} | amount={bid.amount} | ip={ip}"
            )
            messages.success(request, 'Bid submitted successfully.')
            return redirect('procurement:detail', pk=procurement_pk)
    else:
        form = BidSubmitForm()

    return render(request, 'bids/submit.html', {'form': form, 'proc': proc})


@login_required
def open_bid(request, bid_pk):
    """Agency opens a bid after reveal date — logs the event."""
    bid = get_object_or_404(Bid, pk=bid_pk)
    proc = bid.procurement

    if not (request.user.is_agency or request.user.is_staff):
        messages.error(request, 'Not authorised.')
        return redirect('procurement:detail', pk=proc.pk)

    if proc.is_blind():
        messages.error(request, 'Bids are still sealed until the reveal date.')
        return redirect('procurement:detail', pk=proc.pk)

    ip = _get_ip(request)
    ua = request.META.get('HTTP_USER_AGENT', '')[:500]

    BidOpenEvent.objects.create(bid=bid, opened_by=request.user, ip_address=ip, user_agent=ua)
    audit_log.info(
        f"BID_OPENED | user={request.user.username} | bid_id={bid.pk} "
        f"| vendor={bid.vendor.company_name} | ref={proc.reference_no} | ip={ip}"
    )

    return render(request, 'bids/bid_detail.html', {'bid': bid, 'proc': proc})


@login_required
def withdraw_bid(request, bid_pk):
    bid = get_object_or_404(Bid, pk=bid_pk)
    proc = bid.procurement
    vendor = getattr(request.user, 'vendor_profile', None)

    if bid.vendor != vendor:
        messages.error(request, 'You can only withdraw your own bids.')
        return redirect('procurement:detail', pk=proc.pk)

    if not proc.is_accepting_bids():
        messages.error(request, 'Bidding has closed; withdrawal is no longer possible.')
        return redirect('procurement:detail', pk=proc.pk)

    bid.status = Bid.Status.WITHDRAWN
    bid.save()

    ip = _get_ip(request)
    audit_log.info(
        f"BID_WITHDRAWN | user={request.user.username} | bid_id={bid.pk} "
        f"| ref={proc.reference_no} | ip={ip}"
    )
    messages.success(request, 'Bid withdrawn.')
    return redirect('procurement:detail', pk=proc.pk)
