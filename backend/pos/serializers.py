from rest_framework import serializers
from .models import POSSale, POSItem

class POSItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.product_name')

    class Meta:
        model = POSItem
        fields = ['product', 'product_name', 'quantity', 'unit_price', 'line_total']

class POSSaleSerializer(serializers.ModelSerializer):
    items = POSItemSerializer(many=True)

    class Meta:
        model = POSSale
        fields = ['id', 'client', 'timestamp', 'total_amount', 'payment_method', 'served_by', 'items']
        read_only_fields = ['total_amount', 'timestamp']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        pos_sale = POSSale.objects.create(**validated_data)
        
        total = 0
        for item in items_data:
            created_item = POSItem.objects.create(pos_sale=pos_sale, **item)
            total += created_item.line_total
        
        pos_sale.total_amount = total
        pos_sale.save()
        return pos_sale