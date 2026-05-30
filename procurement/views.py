import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Procurement, AwardedContract
from bids.models import Bid

audit_log = logging.getLogger('audit')


@login_required
def procurement_list(request):
    toggle = request.GET.get('view', 'all')
    qs = Procurement.objects.exclude(status='DRAFT')

    if toggle == 'mine' and request.user.is_vendor:
        vendor = getattr(request.user, 'vendor_profile', None)
        if vendor:
            bid_proc_ids = Bid.objects.filter(vendor=vendor).values_list('procurement_id', flat=True)
            qs = qs.filter(id__in=bid_proc_ids)

    return render(request, 'procurement/list.html', {
        'procurements': qs,
        'toggle': toggle,
    })


@login_required
def procurement_detail(request, pk):
    proc = get_object_or_404(Procurement, pk=pk)
    user_bid = None

    if request.user.is_vendor:
        vendor = getattr(request.user, 'vendor_profile', None)
        if vendor:
            user_bid = Bid.objects.filter(procurement=proc, vendor=vendor).first()

    # Audit log: agency/admin viewing a procurement posting
    if request.user.is_agency or request.user.is_staff:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        audit_log.info(
            f"PROCUREMENT_VIEW | user={request.user.username} | ref={proc.reference_no} | ip={ip}"
        )

    bids = None
    if not proc.is_blind() and (request.user.is_agency or request.user.is_staff):
        bids = proc.bids.select_related('vendor').order_by('amount')

    return render(request, 'procurement/detail.html', {
        'proc': proc,
        'user_bid': user_bid,
        'bids': bids,
    })


@login_required
def procurement_create(request):
    if not (request.user.is_agency or request.user.is_staff):
        messages.error(request, 'Only agency users can post procurements.')
        return redirect('procurement:list')

    from .forms import ProcurementForm
    if request.method == 'POST':
        form = ProcurementForm(request.POST)
        if form.is_valid():
            proc = form.save(commit=False)
            proc.posted_by = request.user
            proc.save()
            ip = request.META.get('REMOTE_ADDR', 'unknown')
            audit_log.info(
                f"PROCUREMENT_CREATED | user={request.user.username} | ref={proc.reference_no} | ip={ip}"
            )
            messages.success(request, f'Procurement {proc.reference_no} created.')
            return redirect('procurement:detail', pk=proc.pk)
    else:
        form = ProcurementForm()
    return render(request, 'procurement/form.html', {'form': form, 'action': 'Create'})


@login_required
def award_contract(request, pk):
    if not (request.user.is_agency or request.user.is_staff):
        messages.error(request, 'Not authorised.')
        return redirect('procurement:list')

    proc = get_object_or_404(Procurement, pk=pk)

    if proc.is_blind():
        messages.error(request, 'Bids are still blind. Wait until the reveal date.')
        return redirect('procurement:detail', pk=pk)

    from .forms import AwardContractForm
    if request.method == 'POST':
        form = AwardContractForm(request.POST, procurement=proc)
        if form.is_valid():
            contract = form.save(commit=False)
            contract.procurement = proc
            contract.awarded_by = request.user
            contract.save()
            proc.status = Procurement.Status.AWARDED
            proc.save()

            # Mark winning / losing bids
            Bid.objects.filter(procurement=proc).exclude(
                vendor=contract.awarded_to
            ).update(status=Bid.Status.LOSING)
            Bid.objects.filter(procurement=proc, vendor=contract.awarded_to).update(
                status=Bid.Status.WINNING
            )

            ip = request.META.get('REMOTE_ADDR', 'unknown')
            audit_log.info(
                f"CONTRACT_AWARDED | user={request.user.username} | ref={proc.reference_no} "
                f"| vendor={contract.awarded_to} | value={contract.contract_value} | ip={ip}"
            )
            messages.success(request, 'Contract awarded successfully.')
            return redirect('procurement:detail', pk=pk)
    else:
        form = AwardContractForm(procurement=proc)
    return render(request, 'procurement/award.html', {'form': form, 'proc': proc})
