from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('contracts/', views.AwardedContractListView.as_view(), name='contracts-list'),
    path('contracts/<int:pk>/', views.AwardedContractDetailView.as_view(), name='contracts-detail'),
    path('procurements/', views.ProcurementPublicListView.as_view(), name='procurements-list'),
]
