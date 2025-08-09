from rest_framework import serializers
from .models import *
from django.conf import settings
from cloudinary.utils import cloudinary_url
from decimal import Decimal, ROUND_HALF_UP
# from rest_framework import generics
import json
import cloudinary
from django.http import QueryDict

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'



# serializers.py
# serializers.py
# serializers.py
class ProductSearchSerializer(serializers.ModelSerializer):
    star = serializers.FloatField(source='average_rating', read_only=True)  # Rename average_rating to star

    class Meta:
        model = Product
        fields = ['id', 'images', 'head', 'grand_total', 'description', 'star']


class SuggestedProductSerializer(serializers.ModelSerializer):
    star = serializers.FloatField(source='average_rating', read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'head', 'grand_total', 'star', 'description', 'image']

    def get_image(self, obj):
        images = getattr(obj, 'images', None)
        if images:
            if isinstance(images, list) and len(images) > 0:
                return images[0]
            elif hasattr(images, 'all'):
                first_img = images.all().first()
                if first_img:
                    return getattr(first_img, 'url', None)
        return None





# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'image']

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         try:
#             rep['image'] = instance.image.url if instance.image else None
#         except:
#             rep['image'] = str(instance.image)
#         return rep


# class SubcategoriesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Subcategories
#         fields = ['id', 'name']

# class CategorySerializer(serializers.ModelSerializer):
#     subcategories = SubcategoriesSerializer(many=True, required=False)

#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'image', 'subcategories']

#     def create(self, validated_data):
#         subcategories_data = validated_data.pop('subcategories', [])
#         category = Category.objects.create(**validated_data)
#         for subcat in subcategories_data:
#             Subcategories.objects.create(category=category, **subcat)
#         return category

#     def to_representation(self, instance):
#         rep = super().to_representation(instance)
#         try:
#             rep['image'] = instance.image.url if instance.image else None
#         except:
#             rep['image'] = str(instance.image)

#         # Add subcategories in the response
#         rep['subcategories'] = SubcategoriesSerializer(instance.subcategories.all(), many=True).data
#         return rep


# serializers.py
class SubcategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategories
        fields = ['id', 'sub_name']

# class CategorySerializer(serializers.ModelSerializer):
#     subcategories = SubcategoriesSerializer(many=True, required=False)

#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'image', 'subcategories']

#     def update(self, instance, validated_data):
#         subcategories_data = validated_data.pop('subcategories', None)

#         instance.name = validated_data.get('name', instance.name)
#         instance.image = validated_data.get('image', instance.image)
#         instance.save()

#         if subcategories_data is not None:
#             # Clear existing
#             Subcategories.objects.filter(category=instance).delete()
#             for sub_data in subcategories_data:
#                 Subcategories.objects.create(category=instance, **sub_data)

#         return instance

# class CategorySerializer(serializers.ModelSerializer):
#     subcategories = SubcategoriesSerializer(many=True, required=False)

#     class Meta:
#         model = Category
#         fields = ['id', 'name', 'image', 'subcategories']

#     def __init__(self, *args, **kwargs):
#         initial_data = kwargs.get('data')

#         if isinstance(initial_data, QueryDict):
#             qdict = initial_data.copy()  # mutable
#             raw_subs = qdict.getlist('subcategories')
#             data_dict = dict(qdict)

#             # Flatten all single-value lists like {'name': ['Necklace']} → {'name': 'Necklace'}
#             for key in data_dict:
#                 if isinstance(data_dict[key], list) and len(data_dict[key]) == 1:
#                     data_dict[key] = data_dict[key][0]

#             if raw_subs:
#                 try:
#                     data_dict['subcategories'] = json.loads(raw_subs[0])
#                 except json.JSONDecodeError:
#                     data_dict['subcategories'] = []

#             kwargs['data'] = data_dict

#         super().__init__(*args, **kwargs)

#     def create(self, validated_data):
#         subcategories_data = validated_data.pop('subcategories', [])
#         category = Category.objects.create(**validated_data)
#         for sub_data in subcategories_data:
#             Subcategories.objects.create(category=category, **sub_data)
#         return category

#     def update(self, instance, validated_data):
#         subcategories_data = validated_data.pop('subcategories', None)
#         print("✅ Received subcategories:", subcategories_data)

#         instance.name = validated_data.get('name', instance.name)
#         instance.image = validated_data.get('image', instance.image)
#         instance.save()

#         if subcategories_data is not None:
#             Subcategories.objects.filter(category=instance).delete()
#             for sub_data in subcategories_data:
#                 Subcategories.objects.create(category=instance, **sub_data)

#         return instance
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubcategoriesSerializer(many=True, required=False)
    image = serializers.ImageField(required=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'image', 'subcategories']

    def __init__(self, *args, **kwargs):
        initial_data = kwargs.get('data')
        if isinstance(initial_data, QueryDict):
            qdict = initial_data.copy()
            raw_subs = qdict.getlist('subcategories')
            data_dict = dict(qdict)

            # Flatten single-element lists
            for key in data_dict:
                if isinstance(data_dict[key], list) and len(data_dict[key]) == 1:
                    data_dict[key] = data_dict[key][0]

            if raw_subs:
                try:
                    data_dict['subcategories'] = json.loads(raw_subs[0])
                except json.JSONDecodeError:
                    data_dict['subcategories'] = []

            kwargs['data'] = data_dict

        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        subcategories_data = validated_data.pop('subcategories', [])
        category = Category.objects.create(**validated_data)
        for sub_data in subcategories_data:
            Subcategories.objects.create(category=category, **sub_data)
        return category

    def update(self, instance, validated_data):
        subcategories_data = validated_data.pop('subcategories', None)
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        if subcategories_data is not None:
            Subcategories.objects.filter(category=instance).delete()
            for sub_data in subcategories_data:
                Subcategories.objects.create(category=instance, **sub_data)

        return instance

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
    

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = str(user.id)  # ensure UUID is string
        token['username'] = user.username
        return token




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
    image_url = serializers.SerializerMethodField(read_only=True)  # for GET response
    image = serializers.ImageField(required=False, write_only=True)  # for POST/PUT upload

    class Meta:
        model = UserProfile
        fields = [
            'username',
            'title',
            'full_name',
            'address',
            'date_of_birth',
            'country',
            'phone_number',
            'email',
            'image',        # for uploading image
            'image_url',    # for showing image URL
            'agree'
        ]
        extra_kwargs = {
            'username': {'required': False},
            'agree': {'required': False},
        }

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class UserProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['image'] 


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


# class RecentProductSerializer(serializers.ModelSerializer):
#     first_image = serializers.SerializerMethodField()
#     average_rating = serializers.SerializerMethodField()
#     grand_total = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = ['id', 'head', 'description', 'first_image', 'average_rating', 'grand_total']

#     def get_first_image(self, obj):
#         if obj.images and isinstance(obj.images, list):
#             return obj.images[0] if obj.images else None
#         return None

#     def get_average_rating(self, obj):
#         return obj.average_rating if hasattr(obj, 'average_rating') else None

#     def get_grand_total(self, obj):
#         return str(obj.grand_total) if hasattr(obj, 'grand_total') else None
class RecentProductSerializer(serializers.ModelSerializer):
    first_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()  # ✅ New field

    class Meta:
        model = Product
        fields = [
            'id', 'head', 'description', 'first_image',
            'average_rating', 'grand_total', 'is_wishlisted'
        ]

    def get_first_image(self, obj):
        if obj.images and isinstance(obj.images, list):
            return obj.images[0] if obj.images else None
        return None

    def get_average_rating(self, obj):
        return obj.average_rating if hasattr(obj, 'average_rating') else None

    def get_grand_total(self, obj):
        return str(obj.grand_total) if hasattr(obj, 'grand_total') else None

    def get_is_wishlisted(self, obj):
        user_id = self.context.get('user_id')
        if not user_id:
            return False
        return Wishlist.objects.filter(user_id=user_id, product=obj).exists()
  

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


# class ProductSerializer(serializers.ModelSerializer):
#     stone_price_total = serializers.SerializerMethodField()
#     subtotal = serializers.SerializerMethodField()
#     grand_total = serializers.SerializerMethodField()
#     stones = ProductStoneSerializer(source='productstone_set', many=True, read_only=True)
#     average_rating = serializers.SerializerMethodField()
#     available_stock = serializers.IntegerField(read_only=True)
#     stock_message = serializers.SerializerMethodField()
#     is_wishlisted = serializers.SerializerMethodField()  # ✅ Add this

#     class Meta:
#         model = Product
#         fields = '__all__'

#     def get_stone_price_total(self, obj):
#         return str(obj.stone_price_total)

#     def get_subtotal(self, obj):
#         return str(obj.subtotal)

#     def get_grand_total(self, obj):
#         return str(obj.grand_total)

#     def get_average_rating(self, obj):
#         return getattr(obj, 'average_rating', None)

#     def get_stock_message(self, obj):
#         return "Out of stock" if obj.available_stock == 0 else "In stock"

#     def get_is_wishlisted(self, obj):
#         request = self.context.get('request')
#         if not request:
#             return False

#         user_id = request.query_params.get('user_id')

#         try:
#             user_uuid = uuid.UUID(user_id)
#         except (TypeError, ValueError, AttributeError):
#             return False  # Invalid UUID

#         return Wishlist.objects.filter(user_id=user_uuid, product=obj).exists()

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['images'] = data.get('images') or []
#         return data
# class ProductSerializer(serializers.ModelSerializer):
#     stone_price_total = serializers.SerializerMethodField()
#     subtotal = serializers.SerializerMethodField()
#     grand_total = serializers.SerializerMethodField()
#     stones = serializers.SerializerMethodField()
#     average_rating = serializers.SerializerMethodField()
#     available_stock = serializers.IntegerField(read_only=True)
#     stock_message = serializers.SerializerMethodField()
#     is_wishlisted = serializers.SerializerMethodField()
#     price_details = serializers.SerializerMethodField()
#     metal_details = serializers.SerializerMethodField()
#     stone_details = serializers.SerializerMethodField()

#     category = serializers.SerializerMethodField()
#     occasion = serializers.SerializerMethodField()
#     gender = serializers.SerializerMethodField()
#     metal = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = '__all__'

#     def get_stone_price_total(self, obj):
#         return str(getattr(obj, 'stone_price_total', '0.00'))

#     def get_subtotal(self, obj):
#         return str(getattr(obj, 'subtotal', '0.00'))

#     def get_grand_total(self, obj):
#         return str(getattr(obj, 'grand_total', '0.00'))

#     def get_average_rating(self, obj):
#         return getattr(obj, 'average_rating', 0.0)

#     def get_stock_message(self, obj):
#         return "Out of stock" if obj.available_stock == 0 else "In stock"

#     def get_is_wishlisted(self, obj):
#         request = self.context.get('request')
#         if not request or not hasattr(request, 'user'):
#             return False
#         user = request.user
#         if not user or not user.is_authenticated:
#             return False
#         return Wishlist.objects.filter(user=user, product=obj).exists()

#     def get_category(self, obj):
#         return obj.category.name if obj.category else None

#     def get_occasion(self, obj):
#         return obj.occasion.name if obj.occasion else None

#     def get_gender(self, obj):
#         return obj.gender.name if obj.gender else None

#     def get_metal(self, obj):
#         return obj.metal.name if obj.metal else None

#     def get_stones(self, obj):
#         stones_qs = getattr(obj, 'productstone_set', None)
#         if stones_qs is None:
#             return []
#         serializer = ProductStoneSerializer(stones_qs.all(), many=True, context=self.context)
#         return serializer.data

#     def get_metal_details(self, obj):
#         if not obj.metal:
#             return []

#         metal = obj.metal
#         metal_weight = obj.metal_weight or Decimal('0.000')
#         unit_price = metal.unit_price or Decimal('0.00')
#         metal_price = (metal_weight * unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#         image_url = metal.image.url if metal.image else None

#         return [{
#             "image": image_url,
#             "metal": metal.name,
#             "karat": metal.karat,
#             "unit_price": str(unit_price),
#             "metal_weight": str(metal_weight),
#             "discount": "-",
#             "metal_price": str(metal_price)
#         }]

#     def get_stone_details(self, obj):
#         stone_data = []
#         for ps in obj.productstone_set.all():
#             if not ps.stone:
#                 continue

#             unit_price = ps.stone.unit_price
#             display_unit_price = str(unit_price) if unit_price is not None else "-"
#             stone_price = (
#                 (ps.weight * unit_price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#                 if unit_price is not None else Decimal('0.00')
#             )

#             stone_data.append({
#                 "image": ps.stone.image.url if ps.stone.image else None,
#                 "stone_name": ps.stone.name,
#                 "unit_price": display_unit_price,
#                 "weight": str(ps.weight),
#                 "discount": "-",
#                 "stone_price": str(stone_price),
#             })

#         return stone_data

#     def get_price_details(self, product):
#         def to_decimal(value, default='0.00'):
#             if value is None:
#                 value = default
#             return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#         metal_info = self.get_metal_details(product)
#         metal_detail = metal_info[0] if metal_info else {}

#         stone_price_total = to_decimal(getattr(product, 'stone_price_total', None))
#         making_charge = to_decimal(product.making_charge)
#         designing_charge = to_decimal(product.designing_charge)
#         making_discount = to_decimal(product.making_discount)
#         product_discount = to_decimal(product.product_discount)
#         subtotal = to_decimal(getattr(product, 'subtotal', None))
#         grand_total = to_decimal(getattr(product, 'grand_total', None))
#         gst = to_decimal(product.gst, '3.00')
#         gst_amount = (subtotal * (gst / 100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#         return {
#             **metal_detail,
#             "stone_price": str(stone_price_total),
#             "making_charge": str(making_charge),
#             "designing_charge": str(designing_charge),
#             "making_discount": f"-{making_discount:.2f}",
#             "product_discount": f"-{product_discount:.2f}",
#             f"gst_{int(gst)}_percent": str(gst_amount),
#             "stone_price_total": str(stone_price_total),
#             "subtotal": str(subtotal),
#             "grand_total": str(grand_total),
#             "stones": self.get_stone_details(product),
#             "gst": str(gst),
#         }

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['images'] = data.get('images') or []
#         data['stones'] = data.get('stones') or []
#         return data




# class ProductSerializer(serializers.ModelSerializer):
#     unit_price = serializers.SerializerMethodField()
#     value = serializers.SerializerMethodField()
#     stone_price_total = serializers.SerializerMethodField()
#     subtotal = serializers.SerializerMethodField()
#     grand_total = serializers.SerializerMethodField()
#     stones = serializers.SerializerMethodField()
#     average_rating = serializers.SerializerMethodField()
#     available_stock = serializers.IntegerField(read_only=True)
#     stock_message = serializers.SerializerMethodField()
#     is_wishlisted = serializers.SerializerMethodField()

#     category = serializers.SerializerMethodField()
#     occasion = serializers.SerializerMethodField()
#     gender = serializers.SerializerMethodField()
#     metal = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = '__all__'

#     def get_unit_price(self, obj):
#         """
#         Returns the frozen_unit_price if set and > 0, otherwise metal.unit_price.
#         """
#         if obj.frozen_unit_price and obj.frozen_unit_price > 0:
#             price = obj.frozen_unit_price
#         elif obj.metal and obj.metal.unit_price:
#             price = obj.metal.unit_price
#         else:
#             return "0.00"
#         return str(Decimal(price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

#     def get_value(self, obj):
#         """
#         Calculates value = unit_price * metal_weight.
#         """
#         if obj.frozen_unit_price and obj.frozen_unit_price > 0:
#             unit_price = obj.frozen_unit_price
#         elif obj.metal and obj.metal.unit_price:
#             unit_price = obj.metal.unit_price
#         else:
#             unit_price = Decimal('0.00')

#         metal_weight = obj.metal_weight or Decimal('0.000')
#         value = (unit_price * metal_weight).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
#         return str(value)

#     def get_stone_price_total(self, obj):
#         return str(getattr(obj, 'stone_price_total', Decimal('0.00')))

#     def get_subtotal(self, obj):
#         return str(getattr(obj, 'subtotal', Decimal('0.00')))

#     def get_grand_total(self, obj):
#         return str(getattr(obj, 'grand_total', Decimal('0.00')))

#     def get_average_rating(self, obj):
#         return getattr(obj, 'average_rating', 0.0)

#     def get_stock_message(self, obj):
#         return "Out of stock" if obj.available_stock == 0 else "In stock"

#     def get_is_wishlisted(self, obj):
#         request = self.context.get('request')
#         if not request or not hasattr(request, 'user'):
#             return False
#         user = request.user
#         if not user or not user.is_authenticated:
#             return False
#         return Wishlist.objects.filter(user=user, product=obj).exists()

#     def get_category(self, obj):
#         return obj.category.name if obj.category else None

#     def get_occasion(self, obj):
#         return obj.occasion.name if obj.occasion else None

#     def get_gender(self, obj):
#         return obj.gender.name if obj.gender else None

#     def get_metal(self, obj):
#         return obj.metal.name if obj.metal else None

#     def get_stones(self, obj):
#         stones_qs = getattr(obj, 'productstone_set', None)
#         if stones_qs is None:
#             return []
#         serializer = ProductStoneSerializer(stones_qs.all(), many=True, context=self.context)
#         return serializer.data

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['images'] = data.get('images') or []
#         data['stones'] = data.get('stones') or []
#         return data



# class ProductSerializer(serializers.ModelSerializer):
#     unit_price = serializers.SerializerMethodField()
#     value = serializers.SerializerMethodField()
#     items = serializers.SerializerMethodField()

#     stone_price_total = serializers.SerializerMethodField()
#     subtotal = serializers.SerializerMethodField()
#     grand_total = serializers.SerializerMethodField()
#     stones = serializers.SerializerMethodField()
#     average_rating = serializers.SerializerMethodField()
#     available_stock = serializers.IntegerField(read_only=True)
#     stock_message = serializers.SerializerMethodField()
#     is_wishlisted = serializers.SerializerMethodField()

#     category = serializers.SerializerMethodField()
#     occasion = serializers.SerializerMethodField()
#     gender = serializers.SerializerMethodField()
#     metal = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = '__all__'

#     def get_unit_price(self, obj):
#         if obj.frozen_unit_price and obj.frozen_unit_price > 0:
#             price = obj.frozen_unit_price
#         elif obj.metal and obj.metal.unit_price:
#             price = obj.metal.unit_price
#         else:
#             return "0.00"
#         return str(Decimal(price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

#     def get_value(self, obj):
#         if obj.frozen_unit_price and obj.frozen_unit_price > 0:
#             unit_price = obj.frozen_unit_price
#         elif obj.metal and obj.metal.unit_price:
#             unit_price = obj.metal.unit_price
#         else:
#             unit_price = Decimal('0.00')

#         metal_weight = obj.metal_weight or Decimal('0.000')
#         value = (unit_price * metal_weight).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
#         return str(value)

 
#     def get_items(self, obj):
#         from jewelleryapp.models import Metal  # adjust path if needed
#         items = []

#         # --- METAL card ---
#         if obj.metal:
#             metal = obj.metal
#             unit_price = (
#                 obj.frozen_unit_price if obj.frozen_unit_price and obj.frozen_unit_price > 0
#                 else metal.unit_price
#             )
#             unit_price = Decimal(str(unit_price))
#             metal_weight = obj.metal_weight or Decimal('0.000')
#             value = (unit_price * metal_weight).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#             items.append({
#                 "type": "product",
#                 "name": metal.name,
#                 "subLabel": f"{metal.karat}KT" if metal.karat else "-",
#                 "rate": f"₹ {unit_price}/g",
#                 "weight": f"{metal_weight}g",
#                 "discount": "_",
#                 "value": f"₹ {value}",
#                 "image": metal.image.url if metal.image else None
#             })

#         # --- Get Diamond metal image ---
#         try:
#             diamond = Metal.objects.filter(name__iexact="diamond").first()
#             diamond_image_url = diamond.image.url if diamond and diamond.image else "/assets/Images/ProductDetails/silverbar.png"
#         except:
#             diamond_image_url = "/assets/Images/ProductDetails/silverbar.png"

#         # --- STONE cards ---
#         stone_weight_g = Decimal("0.000")  # total stone weight in grams

#         for ps in obj.productstone_set.all():
#             if not ps.stone:
#                 continue

#             stone = ps.stone
#             weight_ct = ps.weight or Decimal("0.000")
#             weight_g = (weight_ct * Decimal("0.2")).quantize(Decimal("0.003"), rounding=ROUND_HALF_UP)
#             stone_price = ps.get_stone_price() or Decimal("0.00")

#             stone_weight_g += weight_g

#             items.append({
#                 "type": "stone",
#                 "name": "Stone",
#                 "subLabel": None,
#                 "rate": "-",
#                 "weight": f"{weight_ct} ct/{weight_g}g",
#                 "discount": "-",
#                 "value": f"₹ {stone_price.quantize(Decimal('0.01'))}",
#                 "image": diamond_image_url
#             })

#         # --- Making Charges card ---
#         making_charge = obj.making_charge or Decimal("0.00")
#         making_discount = obj.making_discount or Decimal("0.00")

#         items.append({
#             "type": "charges",
#             "label": "Making Charges",
#             "rate": "_",
#             "weight": "_",
#             "discount": f"-₹ {making_discount.quantize(Decimal('0.01'))}" if making_discount > 0 else "-",
#             "value": f"₹ {making_charge.quantize(Decimal('0.01'))}"
#         })

#         # --- Designing Charges card ---
#         designing_charge = obj.designing_charge or Decimal("0.00")

#         if designing_charge > 0:
#             items.append({
#                 "type": "charges",
#                 "label": "Designing Charges",
#                 "rate": "-",
#                 "weight": "-",
#                 "discount": "-",
#                 "value": f"₹ {designing_charge.quantize(Decimal('0.01'))}"
#             })

#         # --- Subtotal with combined weight ---
#         metal_weight = obj.metal_weight or Decimal("0.000")
#         total_weight = (metal_weight + stone_weight_g).quantize(Decimal("0.003"))
#         subtotal = obj.subtotal or Decimal("0.00")

#         items.append({
#             "type": "subtotal",
#             "label": "Sub Total",
#             "rate": "_",
#             "weight": f"{total_weight}g Gross Wt.",
#             "discount": "-",
#             "value": f"₹ {subtotal.quantize(Decimal('0.01'))}"
#         })


#         # --- GST (3% of subtotal) ---
#         gst_rate = Decimal("0.03")
#         gst = (subtotal * gst_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

#         items.append({
#             "type": "gst",
#             "label": "GST",
#             "rate": "",
#             "weight": "_",
#             "discount": "-",
#             "value": f"₹ {gst}"
#         })

#         grand_total = obj.grand_total or Decimal("0.00")
#         grand_total = obj.grand_total or Decimal("0.00")

#         items.append({
#             "type": "charges",
#             "label": "Grand Total",
#             "rate": "_",
#             "weight": "_",
#             "discount": "-",
#             "value": f"₹ {grand_total.quantize(Decimal('0.01'))}"
#         })


#         return items

#     metal_details = serializers.SerializerMethodField()

#     def get_metal_details(self, obj):
#         metal_weight = obj.metal_weight or Decimal("0.000")

#         # Sum all stone weights in grams
#         stone_weight_g = Decimal("0.000")
#         for ps in obj.productstone_set.all():
#             weight_ct = ps.weight or Decimal("0.000")
#             stone_weight_g += (weight_ct * Decimal("0.2"))

#         gross_weight = (metal_weight + stone_weight_g).quantize(Decimal("0.003"))

#         # Start building the content list
#         content = [
#             {
#                 "heading": f"{obj.metal.karat}K" if obj.metal and obj.metal.karat else "-",
#                 "discription": "Karatage"
#             },
#             {
#                 "heading": "Yellow",
#                 "discription": "Material Colour"
#             },
#             {
#                 "heading": f"{gross_weight}g",
#                 "discription": "Gross Weight"
#             },
#             {
#                 "heading": obj.metal.name if obj.metal else "-",
#                 "discription": "Metal"
#             }
#         ]

#         # Conditionally add pendant height if exists
#         if obj.pendant_height is not None:
#             content.append({
#                 "heading": f"{obj.pendant_height} cm",
#                 "discription": "Pendant Height"
#             })

#         # Conditionally add pendant width if exists
#         if obj.pendant_width is not None:
#             content.append({
#                 "heading": f"{obj.pendant_width} cm",
#                 "discription": "Pendant Width"
#             })

#         return {
#             "title": "Metal Details",
#             "content": content
#         }
    
#     def get_diamond_details(self, obj):
#         for ps in obj.productstone_set.all():
#             stone = ps.stone
#             if not stone or stone.name.lower() != "diamond":
#                 continue

#             clarity = stone.clarity or "-"
#             shape = stone.shape or "-"
#             count = ps.count or "-"
#             color = "Yellow"  # Replace with dynamic color if available

#             return {
#                 "title": "Diamond Details",
#                 "content": [
#                     {
#                         "heading": clarity,  # ✅ dynamically from Gemstone.clarity
#                         "discription": "Clarity"
#                     },
#                     {
#                         "heading": color,
#                         "discription": "Diamond Colour"
#                     },
#                     {
#                         "heading": str(count),
#                         "discription": "No of Diamonds"
#                     },
#                     {
#                         "heading": shape,
#                         "discription": "Shape"
#                     }
#                 ]
#             }

#         return None

    
   




#     def get_stone_price_total(self, obj):
#         return str(getattr(obj, 'stone_price_total', Decimal('0.00')))

#     def get_subtotal(self, obj):
#         return str(getattr(obj, 'subtotal', Decimal('0.00')))

#     def get_grand_total(self, obj):
#         return str(getattr(obj, 'grand_total', Decimal('0.00')))

#     def get_average_rating(self, obj):
#         return getattr(obj, 'average_rating', 0.0)

#     def get_stock_message(self, obj):
#         return "Out of stock" if obj.available_stock == 0 else "In stock"

#     def get_is_wishlisted(self, obj):
#         request = self.context.get('request')
#         if not request or not hasattr(request, 'user'):
#             return False
#         user = request.user
#         if not user or not user.is_authenticated:
#             return False
#         return Wishlist.objects.filter(user=user, product=obj).exists()

#     def get_category(self, obj):
#         return obj.category.name if obj.category else None

#     def get_occasion(self, obj):
#         return obj.occasion.name if obj.occasion else None

#     def get_gender(self, obj):
#         return obj.gender.name if obj.gender else None

#     def get_metal(self, obj):
#         return obj.metal.name if obj.metal else None

#     def get_stones(self, obj):
#         stones_qs = getattr(obj, 'productstone_set', None)
#         if stones_qs is None:
#             return []
#         serializer = ProductStoneSerializer(stones_qs.all(), many=True, context=self.context)
#         return serializer.data

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['images'] = data.get('images') or []
#         data['stones'] = data.get('stones') or []
#         return data


# class ProductSerializer(serializers.ModelSerializer):
#     unit_price = serializers.SerializerMethodField()
#     value = serializers.SerializerMethodField()
#     items = serializers.SerializerMethodField()
#     stone_price_total = serializers.SerializerMethodField()
#     subtotal = serializers.SerializerMethodField()
#     grand_total = serializers.SerializerMethodField()
#     stones = serializers.SerializerMethodField()
#     average_rating = serializers.SerializerMethodField()
#     available_stock = serializers.IntegerField(read_only=True)
#     stock_message = serializers.SerializerMethodField()
#     is_wishlisted = serializers.SerializerMethodField()

#     category = serializers.SerializerMethodField()
#     occasion = serializers.SerializerMethodField()
#     gender = serializers.SerializerMethodField()
#     metal = serializers.SerializerMethodField()
#     metal_details = serializers.SerializerMethodField()
#     diamond_details = serializers.SerializerMethodField()
#     general_details = serializers.SerializerMethodField()
#     descriptions = serializers.SerializerMethodField()
#     class Meta:
#         model = Product
#         fields = '__all__'

#     def get_unit_price(self, obj):
#         if obj.frozen_unit_price and obj.frozen_unit_price > 0:
#             price = obj.frozen_unit_price
#         elif obj.metal and obj.metal.unit_price:
#             price = obj.metal.unit_price
#         else:
#             return "0.00"
#         return str(Decimal(price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

#     def get_value(self, obj):
#         if obj.frozen_unit_price and obj.frozen_unit_price > 0:
#             unit_price = obj.frozen_unit_price
#         elif obj.metal and obj.metal.unit_price:
#             unit_price = obj.metal.unit_price
#         else:
#             unit_price = Decimal('0.00')

#         metal_weight = obj.metal_weight or Decimal('0.000')
#         value = (unit_price * metal_weight).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
#         return str(value)

#     def get_items(self, obj):
#         from jewelleryapp.models import Metal
#         items = []

#         if obj.metal:
#             metal = obj.metal
#             unit_price = obj.frozen_unit_price if obj.frozen_unit_price and obj.frozen_unit_price > 0 else metal.unit_price
#             unit_price = Decimal(str(unit_price))
#             metal_weight = obj.metal_weight or Decimal('0.000')
#             value = (unit_price * metal_weight).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

#             items.append({
#                 "type": "product",
#                 "name": f"{metal.color} {metal.name}".strip() if metal.color else metal.name,
#                 "subLabel": f"{metal.karat}KT" if metal.karat else "-",
#                 "rate": f"₹ {unit_price}/g",
#                 "weight": f"{metal_weight}g",
#                 "discount": "_",
#                 "value": f"₹ {value}",
#                 "image": metal.image.url if metal.image else None
#             })

#         try:
#             diamond = Metal.objects.filter(name__iexact="diamond").first()
#             diamond_image_url = diamond.image.url if diamond and diamond.image else "/assets/Images/ProductDetails/silverbar.png"
#         except:
#             diamond_image_url = "/assets/Images/ProductDetails/silverbar.png"

#         stone_weight_g = Decimal("0.000")
#         for ps in obj.productstone_set.all():
#             if not ps.stone:
#                 continue

#             stone = ps.stone
#             weight_ct = ps.weight or Decimal("0.000")
#             weight_g = (weight_ct * Decimal("0.2")).quantize(Decimal("0.003"), rounding=ROUND_HALF_UP)
#             stone_price = ps.get_stone_price() or Decimal("0.00")

#             stone_weight_g += weight_g

#             items.append({
#                 "type": "stone",
#                 "name": stone.name,
#                 "subLabel": None,
#                 "rate": "-",
#                 "weight": f"{weight_ct} ct/{weight_g}g",
#                 "discount": "-",
#                 "value": f"₹ {stone_price.quantize(Decimal('0.01'))}",
#                 "image": diamond_image_url
#             })

#         making_charge = obj.making_charge or Decimal("0.00")
#         making_discount = obj.making_discount or Decimal("0.00")

#         items.append({
#             "type": "charges",
#             "label": "Making Charges",
#             "rate": "_",
#             "weight": "_",
#             "discount": f"-₹ {making_discount.quantize(Decimal('0.01'))}" if making_discount > 0 else "-",
#             "value": f"₹ {making_charge.quantize(Decimal('0.01'))}"
#         })

#         designing_charge = obj.designing_charge or Decimal("0.00")
#         if designing_charge > 0:
#             items.append({
#                 "type": "charges",
#                 "label": "Designing Charges",
#                 "rate": "-",
#                 "weight": "-",
#                 "discount": "-",
#                 "value": f"₹ {designing_charge.quantize(Decimal('0.01'))}"
#             })

#         metal_weight = obj.metal_weight or Decimal("0.000")
#         total_weight = (metal_weight + stone_weight_g).quantize(Decimal("0.003"))
#         subtotal = obj.subtotal or Decimal("0.00")

#         items.append({
#             "type": "subtotal",
#             "label": "Sub Total",
#             "rate": "_",
#             "weight": f"{total_weight}g Gross Wt.",
#             "discount": "-",
#             "value": f"₹ {subtotal.quantize(Decimal('0.01'))}"
#         })

#         gst = (subtotal * Decimal("0.03")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
#         items.append({
#             "type": "gst",
#             "label": "GST",
#             "rate": "",
#             "weight": "_",
#             "discount": "-",
#             "value": f"₹ {gst}"
#         })

#         grand_total = obj.grand_total or Decimal("0.00")
#         items.append({
#             "type": "charges",
#             "label": "Grand Total",
#             "rate": "_",
#             "weight": "_",
#             "discount": "-",
#             "value": f"₹ {grand_total.quantize(Decimal('0.01'))}"
#         })

#         return items

#     def get_metal_details(self, obj):
#         metal_weight = obj.metal_weight or Decimal("0.000")
#         stone_weight_g = sum([(ps.weight or Decimal("0.000")) * Decimal("0.2") for ps in obj.productstone_set.all()])
#         gross_weight = (metal_weight + stone_weight_g).quantize(Decimal("0.003"))

#         content = [
#             {"heading": f"{obj.metal.karat}K" if obj.metal and obj.metal.karat else "-", "discription": "Karatage"},
#             {"heading": "Yellow", "discription": "Material Colour"},
#             {"heading": f"{gross_weight}g", "discription": "Gross Weight"},
#             {"heading": obj.metal.name if obj.metal else "-", "discription": "Metal"}
#         ]

#         if obj.pendant_height is not None:
#             content.append({"heading": f"{obj.pendant_height} cm", "discription": "Pendant Height"})
#         if obj.pendant_width is not None:
#             content.append({"heading": f"{obj.pendant_width} cm", "discription": "Pendant Width"})

#         return {"title": "Metal Details", "content": content}

#     def get_diamond_details(self, obj):
#         for ps in obj.productstone_set.all():
#             stone = ps.stone
#             if not stone or stone.name.lower() != "diamond":
#                 continue

#             clarity = stone.clarity or "-"
#             shape = stone.shape or "-"
#             count = ps.count or "-"
#             color = getattr(stone, 'color', '-')  # <- Get from gemstone if exists
#             # weight_ct = ps.weight or Decimal("0.000")
#             # stone_price = ps.get_stone_price() or Decimal("0.00")

#             return {
#                 "title": "Diamond Details",
#                 "content": [
#                     {"heading": clarity, "discription": "Clarity"},
#                     {"heading": color, "discription": "Diamond Colour"},
#                     {"heading": str(count), "discription": "No of Diamonds"},
#                     {"heading": shape, "discription": "Shape"},
#                     # {"heading": f"{weight_ct} ct", "discription": "Total Carat Weight"},
#                     # {"heading": f"₹ {stone_price.quantize(Decimal('0.01'))}", "discription": "Total Diamond Price"}
#                 ]
#             }
#         return None
    
#     def get_general_details(self, obj):
#         return {
#             "title": "General Details",
#             "content": [
#                 {"heading": "Jewelry", "discription": "Jewellery Type"},
#                 # {"heading": "Yellow", "discription": "Material Colour"},
#                 {"heading": "My Jewellery", "discription": "Brand"},
#                 {"heading": "Best Sellers", "discription": "Collection"},
#                 {"heading": obj.gender.name if obj.gender else "-", "discription": "Gender"},
#                 {"heading": obj.occasion.name if obj.occasion else "-", "discription": "Occasion"}
#             ]
#         }

#     def get_descriptions(self, obj):
#         return {
#             "title": "Description",
#             "content": [
#                 {"description": obj.description}
#             ]
#         }

#     def get_stone_price_total(self, obj):
#         return str(getattr(obj, 'stone_price_total', Decimal('0.00')))

#     def get_subtotal(self, obj):
#         return str(getattr(obj, 'subtotal', Decimal('0.00')))

#     def get_grand_total(self, obj):
#         return str(getattr(obj, 'grand_total', Decimal('0.00')))

#     def get_average_rating(self, obj):
#         return getattr(obj, 'average_rating', 0.0)

#     def get_stock_message(self, obj):
#         return "Out of stock" if obj.available_stock == 0 else "In stock"

#     # def get_is_wishlisted(self, obj):
#     #     request = self.context.get('request')
#     #     if not request or not hasattr(request, 'user'):
#     #         return False
#     #     user = request.user
#     #     if not user or not user.is_authenticated:
#     #         return False
#     #     return Wishlist.objects.filter(user=user, product=obj).exists()
#     def get_is_wishlisted(self, obj):
#         request = self.context.get('request')
#         if not request or not hasattr(request, 'user'):
#             return False

#         user = request.user
#         if not user or not user.is_authenticated:
#             return False

#         # ✅ Check that user is an instance of Register
#         if not isinstance(user, Register):
#             return False

#         return Wishlist.objects.filter(user=user, product=obj).exists()

#     def get_category(self, obj):
#         return obj.category.name if obj.category else None

#     def get_occasion(self, obj):
#         return obj.occasion.name if obj.occasion else None

#     def get_gender(self, obj):
#         return obj.gender.name if obj.gender else None

#     def get_metal(self, obj):
#         return obj.metal.name if obj.metal else None

#     def get_stones(self, obj):
#         stones_qs = getattr(obj, 'productstone_set', None)
#         if stones_qs is None:
#             return []
#         serializer = ProductStoneSerializer(stones_qs.all(), many=True, context=self.context)
#         return serializer.data

#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#         data['images'] = data.get('images') or []
#         data['stones'] = data.get('stones') or []
#         return data



class ProductSerializer(serializers.ModelSerializer):
    unit_price = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    stone_price_total = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    stones = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    available_stock = serializers.IntegerField(read_only=True)
    stock_message = serializers.SerializerMethodField()
    is_wishlisted = serializers.SerializerMethodField()

    category = serializers.SerializerMethodField()
    occasion = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    metal = serializers.SerializerMethodField()
    details = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_unit_price(self, obj):
        if obj.frozen_unit_price and obj.frozen_unit_price > 0:
            price = obj.frozen_unit_price
        elif obj.metal and obj.metal.unit_price:
            price = obj.metal.unit_price
        else:
            return "0.00"
        return str(Decimal(price).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    def get_value(self, obj):
        if obj.frozen_unit_price and obj.frozen_unit_price > 0:
            unit_price = obj.frozen_unit_price
        elif obj.metal and obj.metal.unit_price:
            unit_price = obj.metal.unit_price
        else:
            unit_price = Decimal('0.00')

        metal_weight = obj.metal_weight or Decimal('0.000')
        value = (unit_price * metal_weight).quantize(Decimal('0.001'), rounding=ROUND_HALF_UP)
        return str(value)

    def get_items(self, obj):
        from jewelleryapp.models import Metal
        items = []

        if obj.metal:
            metal = obj.metal
            unit_price = obj.frozen_unit_price if obj.frozen_unit_price and obj.frozen_unit_price > 0 else metal.unit_price
            unit_price = Decimal(str(unit_price))
            metal_weight = obj.metal_weight or Decimal('0.000')
            value = (unit_price * metal_weight).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            items.append({
                "type": "product",
                "name": f"{metal.color} {metal.name}".strip() if metal.color else metal.name,
                "subLabel": f"{metal.karat}KT" if metal.karat else "-",
                "rate": f"\u20b9 {unit_price}/g",
                "weight": f"{metal_weight}g",
                "discount": "_",
                "value": f"\u20b9 {value}",
                "image": metal.image.url if metal.image else None
            })

        try:
            diamond = Metal.objects.filter(name__iexact="diamond").first()
            diamond_image_url = diamond.image.url if diamond and diamond.image else "/assets/Images/ProductDetails/silverbar.png"
        except:
            diamond_image_url = "/assets/Images/ProductDetails/silverbar.png"

        stone_weight_g = Decimal("0.000")
        for ps in obj.productstone_set.all():
            if not ps.stone:
                continue

            stone = ps.stone
            weight_ct = ps.weight or Decimal("0.000")
            weight_g = (weight_ct * Decimal("0.2")).quantize(Decimal("0.003"), rounding=ROUND_HALF_UP)
            stone_price = ps.get_stone_price() or Decimal("0.00")

            stone_weight_g += weight_g

            items.append({
                "type": "stone",
                "name": stone.name,
                "subLabel": None,
                "rate": "-",
                "weight": f"{weight_ct} ct/{weight_g}g",
                "discount": "-",
                "value": f"\u20b9 {stone_price.quantize(Decimal('0.01'))}",
                "image": diamond_image_url
            })

        making_charge = obj.making_charge or Decimal("0.00")
        making_discount = obj.making_discount or Decimal("0.00")

        items.append({
            "type": "charges",
            "label": "Making Charges",
            "rate": "_",
            "weight": "_",
            "discount": f"-\u20b9 {making_discount.quantize(Decimal('0.01'))}" if making_discount > 0 else "-",
            "value": f"\u20b9 {making_charge.quantize(Decimal('0.01'))}"
        })

        designing_charge = obj.designing_charge or Decimal("0.00")
        if designing_charge > 0:
            items.append({
                "type": "charges",
                "label": "Designing Charges",
                "rate": "-",
                "weight": "-",
                "discount": "-",
                "value": f"\u20b9 {designing_charge.quantize(Decimal('0.01'))}"
            })

        metal_weight = obj.metal_weight or Decimal("0.000")
        total_weight = (metal_weight + stone_weight_g).quantize(Decimal("0.003"))
        subtotal = obj.subtotal or Decimal("0.00")

        items.append({
            "type": "subtotal",
            "label": "Sub Total",
            "rate": "_",
            "weight": f"{total_weight}g Gross Wt.",
            "discount": "-",
            "value": f"\u20b9 {subtotal.quantize(Decimal('0.01'))}"
        })

        gst = (subtotal * Decimal("0.03")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        items.append({
            "type": "gst",
            "label": "GST",
            "rate": "",
            "weight": "_",
            "discount": "-",
            "value": f"\u20b9 {gst}"
        })

        grand_total = obj.grand_total or Decimal("0.00")
        items.append({
            "type": "charges",
            "label": "Grand Total",
            "rate": "_",
            "weight": "_",
            "discount": "-",
            "value": f"\u20b9 {grand_total.quantize(Decimal('0.01'))}"
        })

        return items

    def get_details(self, obj):
        details = []

        # Metal Details
        metal_weight = obj.metal_weight or Decimal("0.000")
        stone_weight_g = sum([(ps.weight or Decimal("0.000")) * Decimal("0.2") for ps in obj.productstone_set.all()])
        gross_weight = (metal_weight + stone_weight_g).quantize(Decimal("0.003"))
        metal = obj.metal

        metal_content = [
            {"heading": f"{metal.karat}K" if metal and metal.karat else "-", "discription": "Karatage"},
            {"heading": metal.color if metal and metal.color else "Yellow", "discription": "Material Colour"},
            {"heading": f"{gross_weight}g", "discription": "Gross Weight"},
            {"heading": metal.name if metal else "-", "discription": "Metal"},
        ]
        if obj.pendant_height is not None:
            metal_content.append({"heading": f"{obj.pendant_height} cm", "discription": "Pendant Height"})
        if obj.pendant_width is not None:
            metal_content.append({"heading": f"{obj.pendant_width} cm", "discription": "Pendant Width"})

        details.append({"title": "Metal Details", "content": metal_content})

        # Diamond Details
        for ps in obj.productstone_set.all():
            stone = ps.stone
            if stone and stone.name.lower() == "diamond":
                diamond_content = [
                    {"heading": stone.clarity or "-", "discription": "Clarity"},
                    {"heading": getattr(stone, 'color', '-') or "-", "discription": "Diamond Colour"},
                    {"heading": str(ps.count or "-"), "discription": "No of Diamonds"},
                    {"heading": stone.shape or "-", "discription": "Shape"}
                ]
                details.append({"title": "Diamond Details", "content": diamond_content})
                break

        # General Details
        general_content = [
            {"heading": "Jewelry", "discription": "Jewellery Type"},
            {"heading": "My Jewellery", "discription": "Brand"},
            {"heading": "Best Sellers", "discription": "Collection"},
            {"heading": obj.gender.name if obj.gender else "-", "discription": "Gender"},
            {"heading": obj.occasion.name if obj.occasion else "-", "discription": "Occasion"},
        ]
        details.append({"title": "General Details", "content": general_content})

        # Description
        description = obj.description or "-"
        details.append({"title": "Description", "content": [{"description": description}]})

        return details

    def get_stone_price_total(self, obj):
        return str(getattr(obj, 'stone_price_total', Decimal('0.00')))

    def get_subtotal(self, obj):
        return str(getattr(obj, 'subtotal', Decimal('0.00')))

    def get_grand_total(self, obj):
        return str(getattr(obj, 'grand_total', Decimal('0.00')))

    def get_average_rating(self, obj):
        return getattr(obj, 'average_rating', 0.0)

    def get_stock_message(self, obj):
        return "Out of stock" if obj.available_stock == 0 else "In stock"

    def get_is_wishlisted(self, obj):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return False
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if not isinstance(user, Register):
            return False
        return Wishlist.objects.filter(user=user, product=obj).exists()

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_occasion(self, obj):
        return obj.occasion.name if obj.occasion else None

    def get_gender(self, obj):
        return obj.gender.name if obj.gender else None

    def get_metal(self, obj):
        return obj.metal.name if obj.metal else None

    def get_stones(self, obj):
        stones_qs = getattr(obj, 'productstone_set', None)
        if stones_qs is None:
            return []
        serializer = ProductStoneSerializer(stones_qs.all(), many=True, context=self.context)
        return serializer.data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['images'] = data.get('images') or []
        data['stones'] = data.get('stones') or []
        return data




class NavbarCategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = NavbarCategory
        fields = [
            'id', 'name', 'image', 'order',
            'category', 'material', 'occasion', 'gemstone',
            'is_handcrafted', 'handcrafted_image',
            'is_all_jewellery', 'all_jewellery_image',
            'is_gemstone', 'gemstone_image',
            'occasion_image'  # ✅ Include if you want to POST/GET the image too
        ]

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

class ProductEnquirySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.head', read_only=True)
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductEnquiry
        fields = ['product', 'product_name', 'product_image', 'name', 'email', 'phone', 'message', 'image', 'quantity']
        extra_kwargs = {
            'message': {'required': False, 'allow_blank': True},
            'image': {'required': False, 'allow_null': True},
        }

    def get_product_image(self, obj):
        # If 'images' is a list in the Product model
        if hasattr(obj.product, 'images') and isinstance(obj.product.images, list) and obj.product.images:
            return obj.product.images[0]  # return first image URL
        return None

    def validate_message(self, value):
        if value and value.strip():
            return "I wanted to know more about this: " + value.strip()
        return "I wanted to know more about this"


class FinestProductSerializer(serializers.ModelSerializer):
    first_image = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    grand_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    is_wishlisted = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id',
            'head',
            'description',
            'first_image',
            'average_rating',
            'grand_total',
            'is_wishlisted'
        ]

    def get_first_image(self, obj):
        if obj.images and isinstance(obj.images, list) and len(obj.images) > 0:
            return obj.images[0]
        return None

    def get_average_rating(self, obj):
        return obj.average_rating

    def get_is_wishlisted(self, obj):
        user = self.context.get('user')
        if not user or not hasattr(user, 'id'):
            return False
        return Wishlist.objects.filter(user=user, product=obj).exists()

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


from django.contrib.auth.hashers import check_password

# class AdminLoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         username = data['username']
#         password = data['password']

#         try:
#             admin = AdminLogin.objects.get(username=username)
#         except AdminLogin.DoesNotExist:
#             raise serializers.ValidationError("Invalid username or password")

#         if not check_password(password, admin.password):
#             raise serializers.ValidationError("Invalid username or password")

#         data['admin'] = admin
#         return data

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        try:
            admin = AdminLogin.objects.get(username=username)
        except AdminLogin.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        # ✅ Use Django's check_password function
        if not check_password(password, admin.password):
            raise serializers.ValidationError("Invalid credentials")

        data["admin"] = admin
        return data

class AuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)