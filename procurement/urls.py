from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    path('', views.procurement_list, name='list'),
    path('create/', views.procurement_create, name='create'),
    path('<int:pk>/', views.procurement_detail, name='detail'),
    path('<int:pk>/award/', views.award_contract, name='award'),
]
