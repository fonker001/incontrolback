from django.contrib import admin
from .models import Category, Product, InventoryLog  # Fixed name here

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Added stock_qty to display to help you monitor inventory
    list_display = ('product_name', 'brand_name', 'category', 'selling_price', 'stock_qty', 'is_active')
    list_filter = ('category', 'is_active', 'brand_name')
    search_fields = ('product_name', 'brand_name')
    readonly_fields = ('stock_qty',) # Keep this read-only to let InventoryLog handle updates

@admin.register(InventoryLog)  # Fixed name here
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'supplier', 'quantity_bought', 'cost_price_per_unit', 'total_cost', 'delivery_date')
    list_filter = ('supplier', 'delivery_date')
    readonly_fields = ('total_cost', 'delivery_date')