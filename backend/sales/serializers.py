from rest_framework import serializers
from .models import Sale, SaleItem
from inventory.models import Product

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.product_name')
    brand_name = serializers.ReadOnlyField(source='product.brand_name')

    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'brand_name', 'quantity', 'price_at_sale', 'line_total']
        read_only_fields = ['line_total']

class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    client_name = serializers.ReadOnlyField(source='client.full_name')

    class Meta:
        model = Sale
        fields = [
            'id', 'client', 'client_name', 'sale_date', 
            'total_amount', 'status', 'transaction_id', 
            'shipping_address', 'items'
        ]
        read_only_fields = ['total_amount', 'sale_date']