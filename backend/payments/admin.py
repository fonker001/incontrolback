from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Focus on the Stripe ID and Sale reference for easy reconciliation
    list_display = (
        'stripe_payment_intent_id', 
        'get_sale_id', 
        'amount', 
        'currency', 
        'status', 
        'created_at'
    )
    
    # Filter by status and date to quickly find failed or pending transactions
    list_filter = ('status', 'currency', 'created_at')
    
    # Allow searching by Stripe ID or the Client's email through the Sale relationship
    search_fields = (
        'stripe_payment_intent_id', 
        'sale__id', 
        'sale__client__email',
        'sale__transaction_id'
    )
    
    # Payments should be immutable in the Admin to prevent data tampering
    # Usually, you only want to read these records, not edit them manually.
    readonly_fields = (
        'sale', 
        'stripe_payment_intent_id', 
        'amount', 
        'currency', 
        'created_at'
    )

    def get_sale_id(self, obj):
        return f"Order #{obj.sale.id}"
    get_sale_id.short_description = 'Associated Sale'

    # Color-coding statuses for better scannability
    @admin.display(description='Status')
    def colored_status(self, obj):
        from django.utils.html import format_html
        colors = {
            'succeeded': 'green',
            'pending': 'orange',
            'failed': 'red',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )