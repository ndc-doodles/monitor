from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from decimal import Decimal, ROUND_HALF_UP

from .models import (
    Register, Material, Metal, Gemstone, Product, ProductStone, Occasion,
    Category, Gender, UserVisit, UserProfile, Wishlist, ProductRating,
    Header, NavbarCategory, SearchGif,ProductEnquiry
)

# ------------ Inline Admin for ProductStones ------------
class ProductStoneInline(admin.TabularInline):
    model = ProductStone
    extra = 1

# ------------ Action for Bulk Recalculation ------------
def recalculate_totals(modeladmin, request, queryset):
    for product in queryset:
        product.save()

# ------------ Product Admin with Computed Fields ------------
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'head', 'metal_weight', 'grand_total', 'stone_count', 'category', 'occasion', 'gender')
    inlines = [ProductStoneInline]
    actions = [recalculate_totals]

    def grand_total(self, obj):
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
        except Exception:
            return Decimal('0.00')

    def stone_count(self, obj):
        return obj.productstone_set.count()

# ------------ Register Other Models ------------
admin.site.register(Material)
admin.site.register(Metal)
admin.site.register(Gemstone)
admin.site.register(ProductStone)
admin.site.register(Occasion)
admin.site.register(Category)
admin.site.register(Gender)
admin.site.register(UserVisit)
admin.site.register(UserProfile)
admin.site.register(Wishlist)
admin.site.register(ProductRating)
admin.site.register(Header)
admin.site.register(NavbarCategory)
admin.site.register(SearchGif)

# ------------ Custom UserAdmin for Register Model ------------
@admin.register(Register)
class RegisterAdmin(UserAdmin):
    model = Register
    list_display = ('mobile', 'username', 'is_staff', 'is_superuser')
    search_fields = ('mobile', 'username')
    ordering = ('mobile',)

    fieldsets = (
        (None, {'fields': ('mobile', 'username', 'password')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('mobile', 'username', 'password1', 'password2'),
        }),
    )
@admin.register(ProductEnquiry)
class ProductEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'email', 'phone', 'display_message', 'created_at')

    def display_message(self, obj):
        return obj.get_message_or_default()

    display_message.short_description = 'Message'
