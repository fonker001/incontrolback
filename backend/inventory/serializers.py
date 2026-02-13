from rest_framework import serializers
from .models import Category, Product, InventoryLog
from staff.models import Supplier

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    # Using ImageField handles the validation of actual image files
    image = serializers.ImageField(required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'brand_name', 
            'product_name', 'description', 'selling_price', 
            'image', 'stock_qty', 'is_active'
        ]

class InventoryLogSerializer(serializers.ModelSerializer):
    # These help display names in the dashboard instead of just IDs
    product_details = serializers.ReadOnlyField(source='product.product_name')
    supplier_name = serializers.ReadOnlyField(source='supplier.name')
    total_cost = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = InventoryLog
        fields = [
            'id', 'product', 'product_details', 'supplier', 
            'supplier_name', 'quantity_bought', 'cost_price_per_unit', 
            'total_cost', 'delivery_date'
        ]

    def validate_quantity_bought(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value