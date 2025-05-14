from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductStone

@receiver([post_save, post_delete], sender=ProductStone)
def update_product_totals(sender, instance, **kwargs):
    product = instance.product
    product.save()
