import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Payment
from sales.models import Sale, SaleItem
from inventory.models import Product

class CreatePaymentView(APIView):
    permission_classes=[AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            # --- Create sale directly from request data ---
            shipping_address = request.data.get('shipping_address')
            items_data = request.data.get('items', [])
            phone_number = request.data.get('phone_number')
            
            # Basic validation
            if not shipping_address:
                return Response({'error': 'shipping_address is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            if not items_data:
                return Response({'error': 'items are required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            if not phone_number:
                return Response({'error': 'phone_number is required'}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            # Create sale with default client (ID 1)
            sale = Sale.objects.create(
                client_id=1,  # Default client
                shipping_address=shipping_address,
                status='pending',
                total_amount=0
            )
            
            # Create sale items and calculate total
            total_amount = 0
            for item in items_data:
                sale_item = SaleItem.objects.create(
                    sale=sale,
                    product_id=item.get('product'),
                    quantity=item.get('quantity'),
                    price_at_sale=item.get('price_at_sale')
                )
                total_amount += sale_item.line_total
            
            # Update sale total
            sale.total_amount = total_amount
            sale.save()

            # --- Daraja API integration (your existing code) ---
            # Get Daraja access token
            auth_response = requests.get(
                f"{settings.DARAJA_BASE_URL}/oauth/v1/generate?grant_type=client_credentials",
                auth=(settings.DARAJA_CONSUMER_KEY, settings.DARAJA_CONSUMER_SECRET)
            )
            if auth_response.status_code != 200:
                return Response({'error': 'Failed to get Daraja access token'}, status=500)

            access_token = auth_response.json().get('access_token')

            # Generate password and timestamp
            import base64, datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            raw_password = f"{settings.DARAJA_SHORTCODE}{settings.DARAJA_PASSKEY}{timestamp}"
            stk_password = base64.b64encode(raw_password.encode()).decode('utf-8')

            # Prepare STK Push payload
            stk_payload = {
                "BusinessShortCode": settings.DARAJA_SHORTCODE,
                "Password": stk_password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(sale.total_amount),
                "PartyA": phone_number,
                "PartyB": settings.DARAJA_SHORTCODE,
                "PhoneNumber": phone_number,
                "CallBackURL": f"{settings.HOOK_BASE_URL}/api/payments/daraja-webhook/",
                "AccountReference": f"SALE_{sale.id}",
                "TransactionDesc": f"Payment for Sale #{sale.id}"
            }

            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Call Daraja STK Push API
            response = requests.post(
                f"{settings.DARAJA_BASE_URL}/mpesa/stkpush/v1/processrequest",
                json=stk_payload,
                headers=headers
            )

            if response.status_code != 200:
                return Response({'error': f'Daraja API error: {response.text}'},
                              status=status.HTTP_400_BAD_REQUEST)

            daraja_data = response.json()
            checkout_request_id = daraja_data.get('CheckoutRequestID')
            merchant_request_id = daraja_data.get('MerchantRequestID')

            # Save Payment record
            payment = Payment.objects.create(
                sale=sale,
                amount=sale.total_amount,
                currency='KES',
                status='pending',
                transaction_id=checkout_request_id,
                merchant_request_id=merchant_request_id,
                checkout_request_id=checkout_request_id
            )

            return Response({
                'message': 'STK Push initiated. Check your phone.',
                'sale_id': sale.id,
                'transaction_id': payment.transaction_id,
                'status': payment.status
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            


class DarajaWebhookView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        checkout_request_id = data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        result_code = data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        
        try:
            payment = Payment.objects.get(checkout_request_id=checkout_request_id)
            
            # Prevent duplicate processing
            if payment.status in ['completed', 'failed']:
                return Response({'message': 'Payment already processed'}, 
                              status=status.HTTP_200_OK)
            
            sale = payment.sale

            if result_code == 0:
                payment.status = 'completed'
                sale.status = 'completed'
                sale.save()
                
                # Deduct inventory with flag
                for item in sale.items.all():
                    item.save(deduct_inventory=True)  # This will deduct inventory
            else:
                payment.status = 'failed'
                # Keep sale as 'pending' or mark as 'cancelled'
                sale.status = 'cancelled'
                sale.save()

            payment.save()
        except Payment.DoesNotExist:
            pass  # Optionally log this

        return Response({'message': 'Webhook received'}, status=status.HTTP_200_OK)