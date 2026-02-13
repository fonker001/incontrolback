from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    """Allows adding products directly within the Sale detail page."""
    model = SaleItem
    extra = 1  # Number of empty rows to show by default
    fields = ('product', 'quantity', 'price_at_sale', 'line_total')
    readonly_fields = ('line_total',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_name', 'sale_date', 'total_amount', 'status', 'transaction_id')
    list_filter = ('status', 'sale_date')
    search_fields = ('transaction_id', 'client__first_name', 'client__last_name', 'client__email')
    inlines = [SaleItemInline]
    readonly_fields = ('total_amount', 'sale_date')
    
    fieldsets = (
        ('Order Info', {
            'fields': ('client', 'status', 'transaction_id', 'sale_date')
        }),
        ('Financials', {
            'fields': ('total_amount',)
        }),
        ('Shipping', {
            'fields': ('shipping_address',)
        }),
    )

    def client_name(self, obj):
        # Helper to show full name in the list view
        return f"{obj.client.first_name} {obj.client.last_name}"
    client_name.short_description = 'Client'

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    """Optional: Register standalone if you need to audit individual lines."""
    list_display = ('sale', 'product', 'quantity', 'price_at_sale', 'line_total')
    readonly_fields = ('line_total',)