from rest_framework import serializers
from .models import *


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
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['image'] = instance.image.url if instance.image else None
        return rep


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    metal = MetalSerializer(read_only=True)
    productstone_set = StoneSerializer(many=True, read_only=True)
    image = serializers.ListField(child=serializers.URLField())


    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        # Calculate grand total and other dynamic values
        instance.calculate_grand_total()

        # Get the original representation
        rep = super().to_representation(instance)

        # Add image URLs from the Cloudinary URL field (assuming your image field is a list of Cloudinary data)
        rep['image'] = [img['url'] for img in instance.image] if instance.image else []

        return rep

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


class ProductSerializer(serializers.ModelSerializer):
    stone_names = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
    
    def get_stone_names(self, obj):
        return [stone.name for stone in obj.stones.all()]
    


    
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