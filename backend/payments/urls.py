from django.urls import path
from .views import CreatePaymentView, DarajaWebhookView

urlpatterns = [
    # Initiate an MPESA payment
    path('create-payment/', CreatePaymentView.as_view(), name='create-payment'),

    # Daraja STK Push webhook callback
    path('daraja-webhook/', DarajaWebhookView.as_view(), name='daraja-webhook'),
]
