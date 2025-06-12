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
from rest_framework import serializers
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import random

from django.db.models import Avg
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
    karat = models.FloatField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.karat}K)"

class Gemstone(models.Model):
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
    karat = models.FloatField(null=True, blank=True)
    images = models.JSONField(blank=True, null=True)
    ar_model_glb = models.URLField(blank=True, null=True)
    ar_model_gltf = models.URLField(blank=True, null=True)
    description = models.CharField(max_length=1550, blank=True, null=True)
    pendant_width = models.CharField(max_length=20,blank=True, null=True)
    pendant_height = models.CharField(max_length=20,blank=True, null=True)
    frozen_unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    making_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    making_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    product_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=3)
    handcrafted_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_handcrafted = models.BooleanField(default=False)

    is_classic = models.BooleanField(default=False)  # ✅ New field
    designing_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # ✅ New field
    total_stock = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    
    stones = models.ManyToManyField(Gemstone, related_name="products", blank=True)
    created_at = models.DateTimeField(auto_now_add=True) 

    @property
    def stone_price_total(self):
        total = sum(
            (ps.get_stone_price() or Decimal('0.00') for ps in self.productstone_set.all()),
            Decimal('0.00')
        )
        return total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def subtotal(self):
        if self.frozen_unit_price and self.frozen_unit_price > 0:
            base_price = self.metal_weight * self.frozen_unit_price
        else:
            base_price = self.metal_weight * self.metal.unit_price

        subtotal = (
            base_price
            + self.making_charge
            + self.stone_price_total
            - self.making_discount
            - self.product_discount
        )

        if self.is_classic:
            subtotal += self.designing_charge

        return subtotal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def grand_total(self):
        subtotal = self.subtotal
        total_with_gst = subtotal * (1 + (self.gst / 100))

        if self.is_handcrafted:
            total_with_gst += self.handcrafted_charge

        return total_with_gst.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @property
    def average_rating(self):
        avg = self.ratings.aggregate(avg_rating=Avg('rating')).get('avg_rating')
        if avg is None:
            return 0.0
        return round(avg, 2)
    
    @property
    def available_stock(self):
        return max(self.total_stock - self.sold_count, 0)

    def sell(self, quantity):
        if quantity > self.available_stock:
            raise ValueError("Not enough stock available to sell.")
        self.sold_count += quantity
        self.save()
        return self.available_stock == 0

    def __str__(self):
        return self.head
    

class ProductStone(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stone = models.ForeignKey(Gemstone, on_delete=models.CASCADE, null=True, blank=True)
    count = models.PositiveIntegerField(default=1)
    weight = models.DecimalField(max_digits=10, decimal_places=3, default=0)

    def get_stone_price(self):
        if self.stone and self.weight and self.stone.unit_price:
            return (self.weight * self.stone.unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return None
    
    def __str__(self):
        return self.product.head  

class ProductRating(models.Model):
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # 1 to 5 stars, you can add validation
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} for {self.product.head}"



class NavbarCategory(models.Model):
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    material = models.ForeignKey('Material', on_delete=models.SET_NULL, null=True, blank=True)
    occasion = models.ForeignKey('Occasion', on_delete=models.SET_NULL, null=True, blank=True)
    gemstone = models.ForeignKey('Gemstone', on_delete=models.SET_NULL, null=True, blank=True)
    is_handcrafted = models.BooleanField(default=False)
    handcrafted_image = CloudinaryField('image', folder='handcrafted/', null=True, blank=True)
    is_all_jewellery = models.BooleanField(default=False)
    all_jewellery_image = CloudinaryField('image', folder='all_jewellery/', null=True, blank=True)
    is_gemstone = models.BooleanField(default=False)
    gemstone_image = CloudinaryField('image', folder='gemstone/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    def clean(self):
        fields = [self.category, self.material, self.occasion, self.gemstone, self.is_handcrafted, self.is_all_jewellery, self.is_gemstone]
        count = sum(bool(f) for f in fields)
        if count == 0:
            raise ValidationError("At least one type must be selected.")
        if count > 1:
            raise ValidationError("Only one type can be selected at a time.")

    def __str__(self):
        return self.get_name() or "Unnamed NavbarItem"

    def get_name(self):
        if self.category:
            return self.category.name
        if self.material:
            return self.material.name
        if self.occasion:
            return self.occasion.name
        if self.gemstone:
            return self.gemstone.name
        if self.is_handcrafted:
            return "Handcrafted"
        if self.is_all_jewellery:
            return "All Jewellery"
        if self.is_gemstone:
            return "Gemstone"
        return None

    def get_image(self):
        if self.category and hasattr(self.category, 'image'):
            return self.category.image.url
        if self.material and hasattr(self.material, 'image'):
            return self.material.image.url
        if self.occasion and hasattr(self.occasion, 'image'):
            return self.occasion.image.url
        if self.gemstone and hasattr(self.gemstone, 'image'):
            return self.gemstone.image.url
        if self.is_handcrafted and self.handcrafted_image:
            return self.handcrafted_image.url
        if self.is_all_jewellery and self.all_jewellery_image:
            return self.all_jewellery_image.url
        if self.is_gemstone and self.gemstone_image:
            return self.gemstone_image.url
        return None




class Header(models.Model):
    slider_images = models.JSONField(default=list, null=True, blank=True)
    main_mobile_img = models.JSONField(default=list, null=True, blank=True)
    main_img = models.JSONField(default=list, null=True, blank=True)

    def __str__(self):
        return f"Header with {len(self.slider_images)} images" if self.slider_images else "Empty Header"

class Contact(models.Model):
    number = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    address = models.CharField(max_length=100)

    def __str__(self):
        return self.number
import uuid
class Register(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # UUID primary key
    username = models.OneToOneField(Register, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.BigIntegerField()
    email = models.EmailField(blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    def __str__(self):
        return self.full_name      
class PhoneOTP(models.Model):
    phone = models.CharField(max_length=15, unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone} - {self.otp} - Verified: {self.is_verified}"

    def generate_otp(self):
        import random
        self.otp = str(random.randint(100000, 999999))

# wishlist functioning


class Wishlist(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # A user can't wishlist the same product twice

    def __str__(self):
        return f"{self.user.username} -> {self.product.head}"



class UserVisit(models.Model):
    user = models.ForeignKey('Register', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Visit"
        verbose_name_plural = "User Visits"
        ordering = ['-timestamp']

    def __str__(self):
        if self.user:
            return f"{self.user.username} visited {self.product.head} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
        return f"Anonymous visited {self.product.head} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

class SubCategory(models.Model):
    CATEGORY_TYPES = [
        ('categories', 'Categories'),
        ('occasions', 'Occasions'),
        ('price', 'Price'),
        ('gender', 'Gender'),
    ]
    type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    label = models.CharField(max_length=100)
    icon = models.URLField()

    def __str__(self):
        return f"{self.type} - {self.label}"

# class SearchGif(models.Model):
#     image = models.ImageField(upload_to='gifs/', blank=True, null=True)

#     def __str__(self):
#         return self.image.name if self.image else 'No Image'


class SearchGif(models.Model):
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.image.public_id if self.image else 'No Image'



# class AccountManager(BaseUserManager):
#     def create_user(self, phone, password=None):
#         if not phone:
#             raise ValueError("Users must have a phone number")
#         user = self.model(phone=phone)
#         user.set_unusable_password()
#         user.save(using=self._db)
#         return user

# class Account(AbstractBaseUser):
#     phone = models.CharField(max_length=15, unique=True)
#     is_active = models.BooleanField(default=True)

#     USERNAME_FIELD = 'phone'
#     REQUIRED_FIELDS = []

#     objects = AccountManager()

#     def __str__(self):
#         return self.phone

# class PhoneOTP(models.Model):
#     phone = models.CharField(max_length=15, unique=True)
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_verified = models.BooleanField(default=False)


# class PhoneOTP(models.Model):
#     phone = models.CharField(max_length=15, unique=True)
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_verified = models.BooleanField(default=False)

#     def save(self, *args, **kwargs):
#         import random
#         self.otp = str(random.randint(100000, 999999))
#         super().save(*args, **kwargs)








# class UserVisit(models.Model):
#     user = models.ForeignKey('Register', on_delete=models.CASCADE, null=True, blank=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} visited {self.product.head}"
        



# class CategorySearchHistory(models.Model):
#     user = models.ForeignKey('Register', on_delete=models.CASCADE, related_name="search_history")
#     category = models.ForeignKey('Category', on_delete=models.CASCADE)
#     searched_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         ordering = ['-searched_at']
#         unique_together = ('user', 'category')

#     def __str__(self):
#         return f"{self.user.username} searched {self.category.name}"


# # Tracking visits to products (already in your project)
# class UserVisit(models.Model):
#     user = models.ForeignKey('Register', on_delete=models.CASCADE, null=True, blank=True)
#     product = models.ForeignKey('Product', on_delete=models.CASCADE)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} visited {self.product.head}"



# class NavbarCategory(models.Model):
#     category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
#     material = models.ForeignKey('Material', on_delete=models.SET_NULL, null=True, blank=True)
#     occasion = models.ForeignKey('Occasion', on_delete=models.SET_NULL, null=True, blank=True)
#     gemstone = models.ForeignKey('Gemstone', on_delete=models.SET_NULL, null=True, blank=True)
#     is_handcrafted = models.BooleanField(default=False)
#     handcrafted_image = CloudinaryField('image', folder='handcrafted/', null=True, blank=True)
#     is_all_jewellery = models.BooleanField(default=False)
#     all_jewellery_image = CloudinaryField('image', folder='all_jewellery/', null=True, blank=True)

#     # New fields for gemstone as boolean + image
#     is_gemstone = models.BooleanField(default=False)
#     gemstone_image = CloudinaryField('image', folder='gemstone/', null=True, blank=True)

#     order = models.PositiveIntegerField(default=0)

#     def clean(self):
#         fields = [
#             self.category, self.material, self.occasion, self.gemstone,
#             self.is_handcrafted, self.is_all_jewellery, self.is_gemstone
#         ]
#         count = sum(bool(f) for f in fields)
#         if count == 0:
#             raise ValidationError("At least one type must be selected.")
#         if count > 1:
#             raise ValidationError("Only one type can be selected at a time.")

#     def __str__(self):
#         return self.get_name() or "Unnamed NavbarItem"

#     def get_name(self):
#         if self.category:
#             return self.category.name
#         if self.material:
#             return self.material.name
#         if self.occasion:
#             return self.occasion.name
#         if self.gemstone:
#             return "Gemstone"
#         if self.is_gemstone:
#             return "Gemstone"
#         if self.is_handcrafted:
#             return "Handcrafted"
#         if self.is_all_jewellery:
#             return "All Jewellery"
#         return None

#     def get_image(self):
#         if self.category and hasattr(self.category, 'image') and self.category.image:
#             return self.category.image.url
#         if self.material and hasattr(self.material, 'image') and self.material.image:
#             return self.material.image.url
#         if self.occasion and hasattr(self.occasion, 'image') and self.occasion.image:
#             return self.occasion.image.url
#         if self.gemstone and hasattr(self.gemstone, 'image') and self.gemstone.image:
#             return self.gemstone.image.url
#         if self.is_gemstone and self.gemstone_image:
#             return self.gemstone_image.url
#         if self.is_handcrafted and self.handcrafted_image:
#             return self.handcrafted_image.url
#         if self.is_all_jewellery and self.all_jewellery_image:
#             return self.all_jewellery_image.url
#         return None