from rest_framework import serializers
from .models import *
from django.conf import settings
from cloudinary.utils import cloudinary_url
from decimal import Decimal, ROUND_HALF_UP


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
        fields = ['id', 'name', 'price']
# Serializer for related stones
class ProductStoneSerializer(serializers.ModelSerializer):
    stone_name = serializers.CharField(source='stone.name')

    class Meta:
        model = ProductStone
        fields = ['stone_name', 'quantity', 'price']  # Use the correct field names from your model


# Serializer for Product with dynamic subtotal, grand_total, and stones
class ProductSerializer(serializers.ModelSerializer):
    subtotal = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()
    stone_count = serializers.SerializerMethodField()
    stones = StoneSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'  # You can specify the fields you need if not all are required

    def get_subtotal(self, obj):
        return obj.subtotal  # Calls the property in Product model

    def get_grand_total(self, obj):
        return obj.grand_total  # Calls the property in Product model

    def get_stone_count(self, obj):
        return obj.stone_count 

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