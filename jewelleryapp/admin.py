from django.contrib import admin
from .models import *

class ProductStoneInline(admin.TabularInline):
    model = ProductStone
    extra = 1

def recalculate_totals(modeladmin, request, queryset):
    for product in queryset:
        product.save()

class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'head', 'metal_weight', 'grand_total', 'stone_count', 'category', 'occasion', 'gender')

    def grand_total(self, obj):
        # Calculate grand_total dynamically here
        try:
            metal = obj.metal
            price_per_gram = metal.price_per_gram or Decimal('0.00')
            metal_cost = Decimal(obj.metal_weight or 0) * price_per_gram
            making_charge = Decimal(obj.making_charge or 0)
            handcrafted_charge = Decimal(obj.handcrafted_charge or 0)

            subtotal = metal_cost + making_charge + handcrafted_charge
            making_discount = Decimal(obj.making_discount or 0)
            product_discount = Decimal(obj.product_discount or 0)

            discounted_total = subtotal - making_discount - product_discount
            gst_percent = Decimal(obj.gst or 0)
            gst_amount = discounted_total * gst_percent / Decimal('100.00')

            grand_total = discounted_total + gst_amount
            return grand_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception as e:
            return Decimal('0.00')

    def stone_count(self, obj):
        # Calculate stone count dynamically here
        return obj.productstone_set.count()

admin.site.register(Product, ProductAdmin)

admin.site.register(Material)
admin.site.register(Metal)
admin.site.register(Stone)
admin.site.register(ProductStone)
admin.site.register(Occasion)
admin.site.register(Category)
admin.site.register(Gender)
admin.site.register(Register)
admin.site.register(UserVisit)
admin.site.register(UserProfile)
admin.site.register(Wishlist)