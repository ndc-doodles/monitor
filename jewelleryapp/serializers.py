from rest_framework import serializers
from .models import *

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

class ProductStoneSerializer(serializers.ModelSerializer):
    stone = StoneSerializer(read_only=True)
    class Meta:
        model = ProductStone
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    productstone_set = ProductStoneSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    metal = MetalSerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        instance.calculate_grand_total()
        rep = super().to_representation(instance)
        rep['image'] = instance.image if instance.image else []
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