from django.db import models
from django.core.validators import MinValueValidator
from inventory.models import Product
from staff.models import Client

class POSSale(models.Model):
    """
    Represents a walk-in transaction at a physical location.
    """
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('mobile_money', 'Mobile Money'),
    ]

    # Client is optional for POS (could be a walk-in guest)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='pos_sales')
    timestamp = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    
    # Track which staff member handled the sale
    served_by = models.CharField(max_length=100, help_text="Name or ID of the cashier")

    def __str__(self):
        return f"POS Sale {self.id} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class POSItem(models.Model):
    """
    Individual items scanned or added in the POS interface.
    """
    pos_sale = models.ForeignKey(POSSale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        self.line_total = self.quantity * self.unit_price
        
        # Deduct stock immediately upon physical sale
        if not self.pk:
            if self.product.stock_qty < self.quantity:
                raise ValueError(f"Out of stock: {self.product.product_name}")
            self.product.stock_qty -= self.quantity
            self.product.save()
            
        super().save(*args, **kwargs)