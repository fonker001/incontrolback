from django.db import models
from django.core.validators import MinValueValidator
from staff.models import Supplier

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    """
    The section that displays on the frontend for customers.
    """
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    brand_name = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200)
    description = models.TextField()
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    image = models.ImageField(upload_to='images/products/') # Saves to /media/images/products/
    
    # Stock level (updated automatically when inventory is added)
    stock_qty = models.PositiveIntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand_name', 'product_name']),
        ]

    def __str__(self):
        return f"{self.brand_name} - {self.product_name}"

class InventoryLog(models.Model):
    """
    The 'Supply Side': Tracks deliveries from suppliers.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_history')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='deliveries')
    
    quantity_bought = models.PositiveIntegerField()
    cost_price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    
    delivery_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Calculate total price automatically
        self.total_cost = self.quantity_bought * self.cost_price_per_unit
        
        # Logic to update the main Product stock
        if not self.pk:  # Only on first save (creation)
            self.product.stock_qty += self.quantity_bought
            self.product.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Ref: {self.product.product_name} from {self.supplier.name}"
    
