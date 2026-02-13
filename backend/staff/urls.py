from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RequestOTPView, VerifyOTPView,
    SupplierListView, SupplierCreateView, SupplierDetailView,
    ClientListView, ClientCreateView, ClientDetailView
)

urlpatterns = [
    path('auth/request_otp/', RequestOTPView.as_view(), name='request_otp'),
    path('auth/verify_otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('suppliers/', SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<int:pk>/', SupplierDetailView.as_view(), name='supplier_detail'),

    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
]
