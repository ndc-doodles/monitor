from rest_framework import serializers
from .models import *
from django.conf import settings
from cloudinary.utils import cloudinary_url
from decimal import Decimal, ROUND_HALF_UP
# from rest_framework import generics

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
        model = Stone
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


# class ProductSerializer(serializers.ModelSerializer):
#     stone_names = serializers.SerializerMethodField()

#     class Meta:
#         model = Product
#         fields = '__all__'
    
#     def get_stone_names(self, obj):
#         return [stone.name for stone in obj.stones.all()]

 
class HeaderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Header
        fields = ['id', 'images'] 

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'
    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Register
        fields = ['username', 'password', 'confirmpassword', 'mobile']
    
    def validate(self, data):
        """
        Validate that the password and confirm password match.
        """
        if data['password'] != data['confirmpassword']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'address', 'date_of_birth', 'country', 'phone_number', 'email', 'image']

    def create(self, validated_data):
        # Link the user from Register model when creating a new profile
        user_id = validated_data.pop('user')  # Get user data
        user = Register.objects.get(id=user_id)  # Get the Register model object
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        return user_profile    
        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'



class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'head', 'image', 'grand_total']

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

# class ProductStoneListCreateAPIView(generics.ListCreateAPIView):
#     queryset = ProductStone.objects.all()
#     serializer_class = ProductStoneSerializer

# class ProductStoneDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = ProductStone.objects.all()
#     serializer_class = ProductStoneSerializer


class RecentProductSerializer(serializers.ModelSerializer):
    stone_price_total = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'head', 'category', 'occasion', 'gender', 'metal',
            'metal_weight', 'karat', 'images', 'ar_model_glb', 'ar_model_gltf',
            'frozen_unit_price', 'making_charge', 'making_discount', 'product_discount',
            'gst', 'handcrafted_charge', 'is_handcrafted', 'stones',
            'stone_price_total', 'subtotal', 'grand_total', 'created_at'
        ]

    def get_stone_price_total(self, obj):
        return float(obj.stone_price_total)

    def get_subtotal(self, obj):
        return float(obj.subtotal)

    def get_grand_total(self, obj):
        return float(obj.grand_total)
    

class ProductSerializer(serializers.ModelSerializer):
    stone_price_total = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    stones = ProductStoneSerializer(source='productstone_set', many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_stone_price_total(self, obj):
        return str(obj.stone_price_total)

    def get_subtotal(self, obj):
        return str(obj.subtotal)

    def get_grand_total(self, obj):
        return str(obj.grand_total)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['images'] = data.get('images') or []
        return data