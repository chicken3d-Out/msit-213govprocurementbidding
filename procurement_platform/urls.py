from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('procurement/', include('procurement.urls', namespace='procurement')),
    path('bids/', include('bids.urls', namespace='bids')),
    path('api/v1/', include('api.urls', namespace='api')),
    path('', RedirectView.as_view(url='/procurement/', permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
