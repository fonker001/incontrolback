from django.contrib import admin
from .models import POSSale, POSItem

class POSItemInline(admin.TabularInline):
    model = POSItem
    extra = 0  # We don't want extra empty rows for finished sales
    readonly_fields = ('line_total',)
    fields = ('product', 'quantity', 'unit_price', 'line_total')

@admin.register(POSSale)
class POSSaleAdmin(admin.ModelAdmin):
    # Display key receipt info in the list view
    list_display = ('id', 'timestamp', 'get_client', 'total_amount', 'payment_method', 'served_by')
    list_filter = ('payment_method', 'timestamp', 'served_by')
    search_fields = ('id', 'served_by', 'client__first_name', 'client__last_name')
    
    # Use the inline to show "receipt lines"
    inlines = [POSItemInline]
    
    # Make financials read-only to prevent accidental tampering with historical receipts
    readonly_fields = ('timestamp', 'total_amount')
    
    def get_client(self, obj):
        if obj.client:
            return f"{obj.client.first_name} {obj.client.last_name}"
        return "Walk-in Guest"
    get_client.short_description = 'Customer'

@admin.register(POSItem)
class POSItemAdmin(admin.ModelAdmin):
    list_display = ('pos_sale', 'product', 'quantity', 'unit_price', 'line_total')
    readonly_fields = ('line_total',)