from django.db import models
from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from decimal import Decimal
from cloudinary import uploader
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

from django.contrib.auth import get_user_model
User = get_user_model()
# Base material like Gold, Silver, Diamond, etc.
class Material(models.Model):
    name = models.CharField(max_length=50)

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
    name = models.CharField(max_length=50, blank=True)
    image = CloudinaryField('image', folder="Metal/")
    karat = models.CharField(max_length=20)  # e.g., 22K
    unit_price = models.FloatField(help_text="Price per gram")

    def __str__(self):
        return f"{self.material.name} {self.karat}"


class Stone(models.Model):
    name = models.CharField(max_length=50)
    unit_price = models.FloatField(help_text="Base price per carat")
    discount = models.FloatField(default=0.0, blank=True)  # in percentage
    gemstone_type = models.CharField(max_length=50, blank=True, null=True)  # e.g., Diamond, Emerald
    color_grade = models.CharField(max_length=10, blank=True, null=True)  # e.g., D, E, F
    clarity_grade = models.CharField(max_length=10, blank=True, null=True)  # e.g., VVS1, VS2
    cut_grade = models.CharField(max_length=20, blank=True, null=True)  # e.g., Excellent, Good
    carat_weight = models.FloatField(help_text="Carat weight of the gemstone")  # Actual weight of the gemstone
    image = CloudinaryField('image', folder="Stone/")

    def __str__(self):
        return self.name

    def calculate_price(self):
        """
        Calculate the price of the stone based on its attributes:
        - base price per carat (unit_price)
        - gemstone type
        - color grade
        - clarity grade
        - cut grade
        """
        price = self.unit_price * self.carat_weight  # Initial price based on weight

        # Adjust price based on gemstone type (example: diamond is more expensive than emerald)
        if self.gemstone_type == "Diamond":
            price *= Decimal('2.0')  # Example multiplier for Diamond

        # Adjust price based on color grade (e.g., D is more valuable than F)
        if self.color_grade == "D":
            price *= Decimal('1.5')  # Example multiplier for Color Grade D

        # Adjust price based on clarity grade
        if self.clarity_grade == "VVS1":
            price *= Decimal('1.2')  # Example multiplier for VVS1 clarity
        elif self.clarity_grade == "VS2":
            price *= Decimal('1.1')  # Example multiplier for VS2 clarity

        # Adjust price based on cut grade
        if self.cut_grade == "Excellent":
            price *= Decimal('1.3')  # Example multiplier for Excellent cut
        elif self.cut_grade == "Good":
            price *= Decimal('1.1')  # Example multiplier for Good cut

        # Apply discount if applicable
        price -= (price * self.discount / Decimal('100.0'))

        return price


class Product(models.Model):
    head = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    metal = models.ForeignKey(Metal, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    occasions = models.ManyToManyField(Occasion, blank=True, related_name="products")
    metal_weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Metal weight in grams")
    karat = models.FloatField(null=True, blank=True)
    material_color = models.CharField(max_length=20, null=True, blank=True)
    stones = models.ManyToManyField(Stone, blank=True, related_name='products', help_text="Helper field for quick reference to stones.")
    pendant_height = models.CharField(max_length=20, null=True, blank=True)
    pendant_width = models.CharField(max_length=20, null=True, blank=True)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total weight (auto-calculated)")
    making_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.0'))
    making_discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'), help_text="Discount on making charge %")
    product_discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.0'), help_text="Overall discount %")
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gst = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('3.0'))
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    star_rating = models.DecimalField(max_digits=2, decimal_places=1, default=Decimal('0.0'))
    images = models.JSONField(default=list,blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_stone_weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Total stone weight (in carats)")
    total_stone_count = models.IntegerField(null=True, blank=True, help_text="Total number of stones")

    def calculate_grand_total(self):
        metal_price = self.metal.unit_price * self.metal_weight
        stone_items = self.productstone_set.all()
        total_stone_price = Decimal('0.0')
        total_stone_weight = Decimal('0.0')

        for stone in stone_items:
            total_stone_price += stone.get_stone_price()  # Use the get_stone_price method
            total_stone_weight += stone.weight * stone.count

        making_charge_price = self.making_charge - (self.making_charge * self.making_discount / Decimal('100.0'))

        sub_total = metal_price + total_stone_price + making_charge_price
        sub_total -= (sub_total * self.product_discount / Decimal('100.0'))

        gst_amount = sub_total * self.gst / Decimal('100.0')
        grand_total = sub_total + gst_amount

        self.sub_total = sub_total
        self.gst = self.gst
        self.grand_total = grand_total
        self.gross_weight = self.metal_weight + (total_stone_weight * Decimal('0.2'))
        self.total_stone_weight = total_stone_weight
        self.total_stone_count = sum(stone.count for stone in stone_items)

        self.save()

        return {
            "metal_price": metal_price,
            "stone_price": total_stone_price,  
            "making_charge_after_discount": making_charge_price,
            "sub_total": sub_total,
            "gst": gst_amount,
            "grand_total": grand_total,
            "gross_weight": self.gross_weight,
            "total_stone_weight": total_stone_weight,
            "total_stone_count": self.total_stone_count
        }

    # def save(self, *args, **kwargs):
    #     """Override save method to handle multiple image uploads and deletion of old images"""
    #     if self.images:
    #         # If images exist and have changed, delete old images from Cloudinary
    #         if hasattr(self, '_old_image') and self._old_image != self.images:
    #             for old_image_url in self._old_image:
    #                 public_id = old_image_url.split("/")[7]  # Extract public_id from the URL
    #                 if public_id:
    #                     try:
    #                         uploader.destroy(public_id)  # Delete old image from Cloudinary
    #                     except Exception as e:
    #                         print(f"Error deleting old image: {e}")

    #     # If new images are provided, upload them to Cloudinary
    #     if self.image:
    #         uploaded_images = []
    #         for img_data in self.image:
    #             if 'file' in img_data:
    #                 upload_result = uploader.upload(img_data['file'])
    #                 uploaded_images.append(upload_result["secure_url"])  # Store only the URL

    #         self.image = uploaded_images  # Store only URLs in the image field

    #     super().save(*args, **kwargs)

    def __str__(self):
        return self.head


class ProductStone(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stone = models.ForeignKey(Stone, on_delete=models.CASCADE)
    count = models.IntegerField()
    weight = models.FloatField(help_text="Weight of one stone in carat")

    def get_formatted_single_stone_weight(self):
        gram = self.weight * 0.2
        return f"1 stone: {self.weight:.3f} ct / {gram:.3f} g"

    def get_stone_price(self):
        """Calculate the total price of the stones based on the unit price and count."""
        stone_price = self.stone.calculate_price()
        total_price = stone_price * self.count  # Multiply by count of stones
        return total_price

    def __str__(self):
        return f"{self.product.head} - {self.stone.name}"


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
