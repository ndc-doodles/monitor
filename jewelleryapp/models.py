from django.db import models
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from cloudinary import uploader
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.utils import timezone 
from django.contrib.auth import get_user_model
User = get_user_model()
from decimal import Decimal, ROUND_HALF_UP
# Base material like Gold
# , Silver, Diamond, etc.
class Material(models.Model):
    name = models.CharField(max_length=50)
    image = CloudinaryField('image', folder="Material/")

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)
    image = CloudinaryField('image', folder="category/")

    def __str__(self):
        return self.name

class Occasion(models.Model):
    name = models.CharField(max_length=50)
    image = CloudinaryField('image', folder='Occasions')

    def __str__(self):
        return self.name

class Gender(models.Model):
    name = models.CharField(max_length=20)  # e.g., Men, Women, Unisex
    image = CloudinaryField('image', folder='gender')

    def __str__(self):
        return self.name

class Metal(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = CloudinaryField('image', folder='metal')
    karat = models.FloatField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.karat}K)"

class Stone(models.Model):
    name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = CloudinaryField('image', folder='stones')

    def calculate_price(self, weight):
        return weight * self.unit_price

    def __str__(self):
        return self.name

# --- Product Model ---
class Product(models.Model):
    head = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    occasion = models.ForeignKey(Occasion, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE)
    metal = models.ForeignKey(Metal, on_delete=models.CASCADE)
    
    metal_weight = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    karat = models.FloatField()
    images = models.JSONField(blank=True, null=True)
    ar_model_glb = models.URLField(blank=True, null=True)
    ar_model_gltf = models.URLField(blank=True, null=True)

    # Instead of metal.unit_price directly, we freeze the unit price on creation
    frozen_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    making_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    making_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=3)
    handcrafted_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_handcrafted = models.BooleanField(default=False)


    stones = models.ManyToManyField(Stone, related_name="products", blank=True)

    @property
    def stone_price_total(self):
        total = sum(
            ps.get_stone_price() or Decimal('0.00')
            for ps in self.productstone_set.all()
            if ps.stone is not None
        )
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def subtotal(self):
        subtotal = (
            self.metal_weight * self.frozen_unit_price
            + self.making_charge
            + self.stone_price_total
            - self.making_discount
            - self.product_discount
        )
        return subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def grand_total(self):
        subtotal = self.subtotal
        total_with_gst = subtotal * (1 + (self.gst / 100))
        if self.is_handcrafted:
            total_with_gst += self.handcrafted_charge
        return total_with_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)



class ProductStone(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stone = models.ForeignKey(Stone, on_delete=models.CASCADE, null=True, blank=True)
    count = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    def get_stone_price(self):
        if self.stone and self.weight and self.stone.unit_price:
            return (self.weight * self.stone.unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return None

#     head = models.CharField(max_length=255)
#     metal = models.ForeignKey(Metal, on_delete=models.CASCADE)
#     metal_weight = models.DecimalField(max_digits=10, decimal_places=2)
#     karat = models.FloatField()
#     making_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
#     making_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
#     product_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0, null=True, blank=True)
#     gst = models.DecimalField(max_digits=5, decimal_places=2, default=3.0)
#     handcrafted_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     is_handcrafted = models.BooleanField(default=False)
#     images = models.JSONField(default=list, null=True, blank=True)
#     ar_model_glb = models.CharField(max_length=255, null=True, blank=True)
#     ar_model_gltf = models.CharField(max_length=255, null=True, blank=True)
#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     # NEW FIELDS (store in DB)
#     subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

#     @property
#     def total_stone_weight(self):
#         total = sum([ps.count * ps.weight for ps in self.productstone_set.all()])
#         return round(total, 2) if total else None

#     @property
#     def total_stone_count(self):
#         count = sum([ps.count for ps in self.productstone_set.all()])
#         return count if count else None

#     def calculate_subtotal(self):
#         metal_cost = self.metal.calculate_price_per_gram() * self.metal_weight
#         making_cost = self.making_charge
#         stone_total = sum([ps.get_stone_price() for ps in self.productstone_set.all()])

#         total = metal_cost + Decimal(stone_total) + making_cost
#         if self.is_handcrafted:
#             total += self.handcrafted_charge

#         if self.making_discount:
#             total -= (making_cost * (self.making_discount / Decimal(100)))
#         if self.product_discount:
#             total -= (total * (self.product_discount / Decimal(100)))

#         return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#     def calculate_grand_total(self):
#         subtotal = self.calculate_subtotal()
#         gst_amount = subtotal * (self.gst / Decimal(100))
#         return (subtotal + gst_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#     def save(self, *args, **kwargs):
#         self.subtotal = self.calculate_subtotal()
#         self.grand_total = self.calculate_grand_total()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.head


# class ProductStone(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     stone = models.ForeignKey(Stone, on_delete=models.CASCADE)
#     count = models.IntegerField()
#     weight = models.FloatField(help_text="Weight of one stone in carat")

#     def get_formatted_single_stone_weight(self):
#         gram = self.weight * 0.2  # Convert carat to grams
#         return f"1 stone: {self.weight:.3f} ct / {gram:.3f} g"

#     def get_stone_price(self):
#         stone_price = self.stone.calculate_price()
#         return stone_price * self.count

#     def __str__(self):
#         return f"{self.product.head} - {self.stone.name}"

class Header(models.Model):
    images = models.JSONField(default=list, null=True, blank=True)

    def __str__(self):
        return self.images

class Contact(models.Model):
    number = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.number

class Register(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    confirmpassword = models.CharField(max_length=128)
    mobile = models.BigIntegerField()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Ensure passwords match before saving
        if self.password != self.confirmpassword:
            raise ValidationError("Passwords do not match")
        
        # Hash the password before saving
        self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
class UserVisit(models.Model):
    user = models.ForeignKey('Register', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} visited {self.product.head}"
        

class UserProfile(models.Model):
    # Link to the Register model (One-to-One relationship)
    user = models.OneToOneField(Register, on_delete=models.CASCADE, related_name='profile')

    # The fields in the UserProfile model
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.BigIntegerField()  # You can fetch this from the Register model
    email = models.EmailField(blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.full_name       


# wishlist functioning


class Wishlist(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # A user can't wishlist the same product twice

    def __str__(self):
        return f"{self.user.username} -> {self.product.head}"

