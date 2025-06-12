from rest_framework import serializers
from .models import *
from django.conf import settings
from cloudinary.utils import cloudinary_url
from decimal import Decimal, ROUND_HALF_UP
# from rest_framework import generics
import json
import cloudinary

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url if instance.image else None
        return rep

class MetalSerializer(serializers.ModelSerializer):
    material = MaterialSerializer(read_only=True)
    class Meta:
        model = Metal
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url if instance.image else None
        return rep

class StoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gemstone
        fields = ['id', 'name', 'unit_price']


# Serializer for related stones
class ProductStoneSerializer(serializers.ModelSerializer):
    stone = StoneSerializer(read_only=True)
    stone_price = serializers.SerializerMethodField()

    class Meta:
        model = ProductStone
        fields = ['id', 'product', 'stone', 'count', 'weight', 'stone_price']

    def get_stone_price(self, obj):
        price = obj.get_stone_price()
        return str(price) if price else None


# Serializer for Product with dynamic subtotal, grand_total, and stones

class OccasionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occasion
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url if instance.image else None
        return rep
    
class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gender
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url if instance.image else None
        return rep

 
class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = ['id', 'slider_images', 'main_img', 'main_mobile_img']
        
class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
    
# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Register
#         fields = ['username', 'password', 'confirmpassword', 'mobile']
    
#     def validate(self, data):
#         """
#         Validate that the password and confirm password match.
#         """
#         if data['password'] != data['confirmpassword']:
#             raise serializers.ValidationError("Passwords do not match")
#         return data

# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     confirmpassword = serializers.CharField(write_only=True)

#     class Meta:
#         model = Register
#         fields = ['id', 'username', 'password', 'confirmpassword', 'mobile']
#         read_only_fields = ['id']

#     def validate(self, data):
#         if data['password'] != data['confirmpassword']:
#             raise serializers.ValidationError("Passwords do not match")
#         return data



# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ['full_name', 'address', 'date_of_birth', 'country', 'phone_number', 'email', 'image']

#     def create(self, validated_data):
#         # Link the user from Register model when creating a new profile
#         user_id = validated_data.pop('user')  # Get user data
#         user = Register.objects.get(id=user_id)  # Get the Register model object
#         user_profile = UserProfile.objects.create(user=user, **validated_data)
#         return user_profile    


# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Register
#         fields = ['id', 'username', 'mobile']


# class UserProfileSerializer(serializers.ModelSerializer):
#     username = serializers.SerializerMethodField()

#     class Meta:
#         model = UserProfile
#         fields = ['id', 'username', 'full_name', 'phone_number', 'email', 'address', 'date_of_birth', 'country', 'image']

#     def get_username(self, obj):
#         return f"user{obj.username.username}"      

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = ['id', 'username', 'mobile']


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_username(self, obj):
        return f"user{obj.username.username}"  

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'



# class ProductShortSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = ['id', 'head', 'images', 'grand_total']
class ProductShortSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='head', read_only=True)
    product_image = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    stock_message = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'product_name', 'product_image', 'price', 'stock_message']

    def get_product_image(self, obj):
        return obj.images[0] if obj.images else None

    def get_price(self, obj):
        return str(obj.grand_total)

    def get_stock_message(self, obj):
        return "Out of stock" if obj.available_stock == 0 else "In stock"

# class WishlistSerializer(serializers.ModelSerializer):
#     product = ProductShortSerializer(read_only=True)
#     product_id = serializers.PrimaryKeyRelatedField(
#         queryset=Product.objects.all(),
#         source='product',
#         write_only=True
#     )
#     user_id = serializers.IntegerField(write_only=True)

#     class Meta:
#         model = Wishlist
#         fields = ['id', 'user_id', 'product', 'product_id', 'added_at']     
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductShortSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user_id', 'product', 'product_id', 'added_at']


class RecentProductSerializer(serializers.ModelSerializer):
    first_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'head', 'description', 'first_image', 'average_rating', 'grand_total']

    def get_first_image(self, obj):
        if obj.images and isinstance(obj.images, list):
            return obj.images[0] if obj.images else None
        return None

    def get_average_rating(self, obj):
        return obj.average_rating if hasattr(obj, 'average_rating') else None

    def get_grand_total(self, obj):
        return str(obj.grand_total) if hasattr(obj, 'grand_total') else None
    

class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = ['id', 'product', 'rating', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ClassicProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'head', 'images', 'grand_total']


class ProductSerializer(serializers.ModelSerializer):
    stone_price_total = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    stones = ProductStoneSerializer(source='productstone_set', many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    available_stock = serializers.IntegerField(read_only=True)
    stock_message = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()  # ✅ Add this

    class Meta:
        model = Product
        fields = '__all__'

    def get_stone_price_total(self, obj):
        return str(obj.stone_price_total)

    def get_subtotal(self, obj):
        return str(obj.subtotal)

    def get_grand_total(self, obj):
        return str(obj.grand_total)

    def get_average_rating(self, obj):
        return getattr(obj, 'average_rating', None)

    def get_stock_message(self, obj):
        return "Out of stock" if obj.available_stock == 0 else "In stock"

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        user_id = request.query_params.get('user_id')
        if not user_id:
            return False
        return Wishlist.objects.filter(user_id=user_id, product=obj).exists()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['images'] = data.get('images') or []
        return data


class NavbarCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NavbarCategory
        fields = ['id', 'name', 'image', 'order', 'category', 'material', 'occasion',
                  'gemstone', 'is_handcrafted', 'handcrafted_image',
                  'is_all_jewellery', 'all_jewellery_image',
                  'is_gemstone', 'gemstone_image']

    def get_name(self, obj):
        return obj.get_name()

    def get_image(self, obj):
        return obj.get_image()
    

class SimpleLabelIconSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    label = serializers.CharField()
    icon = serializers.CharField()

class NavbarCategoryMegaSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    mega = serializers.SerializerMethodField()

    class Meta:
        model = NavbarCategory
        fields = ['id', 'title', 'image', 'description', 'mega']

    def get_title(self, obj):
        return obj.get_name()

    def get_image(self, obj):
        return obj.get_image()

    def get_description(self, obj):
        # Customize description as needed
        return "Elegant handcrafted gold jewelry."

    def get_mega(self, obj):
        # Return subcategory lists depending on obj id or other fields
        if obj.id == 1:  # For example, "All Jewelry"
            return {
                "Category": [
                    { "id": 1, "label": "All Jewellery", "icon": "/public/assets/Images/subcategory/1.png" },
                    { "id": 2, "label": "Bangles", "icon": "/public/assets/Images/subcategory/1.png" },
                    { "id": 3, "label": "Nose Pin", "icon": "/public/assets/Images/subcategory/1.png" },
                    { "id": 4, "label": "Finger Rings", "icon": "/public/assets/Images/subcategory/1.png" }
                ],
                "Occasions": [
                    { "id": 1, "label": "Office wear", "icon": "/public/assets/Images/subcategory/occasions/o1.png" },
                    { "id": 2, "label": "Casual wear", "icon": "/public/assets/Images/subcategory/occasions/o2.png" },
                    { "id": 3, "label": "Modern wear", "icon": "/public/assets/Images/subcategory/occasions/o3.png" },
                    { "id": 4, "label": "Traditional wear", "icon": "/public/assets/Images/subcategory/occasions/o4.png" }
                ],
                "Price": [
                    { "id": 1, "label": "<25K", "icon": "/public/assets/Images/subcategory/rate/r1.png" },
                    { "id": 2, "label": "25K - 50K", "icon": "/public/assets/Images/subcategory/rate/r2.png" },
                    { "id": 3, "label": "50K - 1L", "icon": "/public/assets/Images/subcategory/rate/r3.png" },
                    { "id": 4, "label": "1L & Above", "icon": "/public/assets/Images/subcategory/rate/r4.png" }
                ],
                "Gender": [
                    { "id": 1, "label": "Women", "icon": "/public/assets/Images/subcategory/gender/f.png" },
                    { "id": 2, "label": "Men", "icon": "/public/assets/Images/subcategory/gender/m.png" },
                    { "id": 3, "label": "Kid", "icon": "/public/assets/Images/subcategory/gender/k.png" }
                ]
            }
        elif obj.id == 2:  # "Gold"
            return {
                "Category": [
                    { "id": 10, "label": "Gold Rings", "icon": "/public/assets/Images/subcategory/1.png" },
                    { "id": 11, "label": "Gold Bangles", "icon": "/public/assets/Images/subcategory/1.png" }
                ],
                "Occasions": [
                    { "id": 5, "label": "Wedding", "icon": "/public/assets/Images/subcategory/occasions/o5.png" }
                ],
                "Price": [
                    { "id": 1, "label": "<25K", "icon": "/public/assets/Images/subcategory/rate/r1.png" },
                    { "id": 2, "label": "25K - 50K", "icon": "/public/assets/Images/subcategory/rate/r2.png" },
                    { "id": 3, "label": "50K - 1L", "icon": "/public/assets/Images/subcategory/rate/r3.png" },
                    { "id": 4, "label": "1L & Above", "icon": "/public/assets/Images/subcategory/rate/r4.png" }
                ],
                "Gender": [
                    { "id": 1, "label": "Women", "icon": "/public/assets/Images/subcategory/gender/f.png" },
                    { "id": 2, "label": "Men", "icon": "/public/assets/Images/subcategory/gender/m.png" },
                    { "id": 3, "label": "Kid", "icon": "/public/assets/Images/subcategory/gender/k.png" }
                ]
            }
        else:
            return {
                "Category": [],
                "Occasions": [],
                "Price": [],
                "Gender": []
            }

class FinestProductSerializer(serializers.ModelSerializer):
    first_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Product
        fields = ['id', 'head', 'description', 'first_image', 'average_rating', 'grand_total']

    def get_first_image(self, obj):
        if obj.images and isinstance(obj.images, list) and len(obj.images) > 0:
            return obj.images[0]
        return None

    def get_average_rating(self, obj):
        return obj.average_rating

# serializers.py
class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'label', 'icon']



class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class PopularProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'head', 'image']

    def get_image(self, obj):
        if obj.images and isinstance(obj.images, list):
            return obj.images[0] if obj.images else None
        elif obj.images and isinstance(obj.images, dict):
            return next(iter(obj.images.values()), None)
        return None

class SearchGifSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = SearchGif
        fields = ['id', 'image']

    def get_image(self, obj):
        if obj.image:
            return f"https://res.cloudinary.com/{cloudinary.config().cloud_name}/{obj.image}"
        return None
    

class SimpleProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'head', 'image']

    def get_image(self, obj):
        # Assuming your product has a related images field or single image field
        # Adjust this logic based on your actual Product model
        first_image = obj.images.first()
        return first_image.image.url if first_image else None
    
class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)


# class PhoneSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=15)

# class VerifyOTPSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=15)
#     otp = serializers.CharField(max_length=6)
# class PhoneSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=15)

# class VerifyOTPSerializer(serializers.Serializer):
#     phone = serializers.CharField(max_length=15)
#     otp = serializers.CharField(max_length=6)


# class CategoryNameSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['name']


# class PopularProductSerializer(serializers.ModelSerializer):
#     image = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = ['head', 'image']

#     def get_image(self, obj):
#         images = obj.images
#         if isinstance(images, list) and images:
#             return images[0]  # Return first image from list
#         elif isinstance(images, dict) and images:
#             return next(iter(images.values()), None)  # Return first value from dict
#         return None  # No image


