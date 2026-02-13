from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import SaleItem, Sale

@receiver([post_save, post_delete], sender=SaleItem)
def update_sale_total(sender, instance, **kwargs):
    """
    Automatically recalculates the Sale total_amount whenever 
    a SaleItem is added, updated, or removed.
    """
    sale = instance.sale
    # Aggregate the sum of all line_totals for this sale
    aggregate = SaleItem.objects.filter(sale=sale).aggregate(total=Sum('line_total'))
    sale.total_amount = aggregate['total'] or 0.00
    sale.save()