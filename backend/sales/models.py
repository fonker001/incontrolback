from django.db import models
from django.core.validators import MinValueValidator
from staff.models import Client
from inventory.models import Product

class Sale(models.Model):
    """
    Represents an overall online transaction.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='sales')
    sale_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Tracking for shipping/online specifics
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    shipping_address = models.TextField()

    def __str__(self):
        return f"Sale {self.id} - {self.client.full_name}"

class SaleItem(models.Model):
    """
    Individual products within a single Sale.
    """
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price_at_sale = models.DecimalField(max_digits=12, decimal_places=2) # Price can change, so we lock it here
    line_total = models.DecimalField(max_digits=12, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate line total
        self.line_total = self.quantity * self.price_at_sale
        
        # Check if this is being called from webhook
        deduct_inventory = kwargs.pop('deduct_inventory', False)
        
        if deduct_inventory:
            # Refresh sale status to ensure we have the latest
            self.sale.refresh_from_db()
            if self.sale.status == 'completed':
                if self.product.stock_qty < self.quantity:
                    raise ValueError(f"Insufficient stock for {self.product.product_name}")
                self.product.stock_qty -= self.quantity
                self.product.save()
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity} x {self.product.product_name}"