from django.urls import path
from . import views

app_name = 'bids'

urlpatterns = [
    path('submit/<int:procurement_pk>/', views.submit_bid, name='submit'),
    path('open/<int:bid_pk>/', views.open_bid, name='open'),
    path('withdraw/<int:bid_pk>/', views.withdraw_bid, name='withdraw'),
]
