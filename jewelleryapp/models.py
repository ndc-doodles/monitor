from django.db import models
from cloudinary.models import CloudinaryField

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
    unit_price = models.FloatField(help_text="Price per carat")
    discount = models.FloatField(default=0.0, blank=True)  # in percentage
    image = CloudinaryField('image', folder="Stone/")

    def __str__(self):
        return self.name


class Product(models.Model):
    head = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    metal = models.ForeignKey(Metal, on_delete=models.CASCADE)
    gender = models.ForeignKey(Gender, on_delete=models.SET_NULL, null=True, blank=True)
    occasions = models.ManyToManyField(Occasion, blank=True, related_name="products")
    metal_weight = models.FloatField(help_text="Metal weight in grams")
    karat = models.CharField(max_length=20, null=True, blank=True)
    material_color = models.CharField(max_length=20, null=True, blank=True)

    stones = models.ManyToManyField(Stone, blank=True, related_name='products', help_text="Helper field for quick reference to stones.")

    pendant_height = models.CharField(max_length=20, null=True, blank=True)
    pendant_width = models.CharField(max_length=20, null=True, blank=True)
    gross_weight = models.FloatField(null=True, blank=True, help_text="Total weight (auto-calculated)")
    stone_price = models.FloatField(null=True, blank=True)
    making_charge = models.FloatField(default=0.0)
    making_discount = models.FloatField(default=0.0, help_text="Discount on making charge %")
    product_discount = models.FloatField(default=0.0, help_text="Overall discount %")
    sub_total = models.FloatField(null=True, blank=True)
    gst = models.FloatField(default=3.0)
    grand_total = models.FloatField(null=True, blank=True)
    star_rating = models.FloatField(default=0.0)
    image = models.JSONField(default=list, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_grand_total(self):
        metal_price = self.metal.unit_price * self.metal_weight

        stone_items = self.productstone_set.all()
        total_stone_price = 0
        stone_details = []
        total_stone_weight = 0

        for stone in stone_items:
            one_price = stone.stone.unit_price * stone.weight
            one_price -= (one_price * stone.stone.discount / 100)
            total_price = one_price * stone.count
            total_stone_price += total_price

            total_stone_weight += stone.weight * stone.count
            stone_details.append({
                "stone": stone.stone.name,
                "count": stone.count,
                "one_weight_ct": f"{stone.weight:.3f} ct",
                "one_weight_g": f"{stone.weight * 0.2:.3f} g",
                "total_weight": f"{stone.weight * stone.count:.3f} ct",
                "total_price": total_price
            })

        making_charge_price = self.making_charge - (self.making_charge * self.making_discount / 100)
        sub_total = metal_price + total_stone_price + making_charge_price
        sub_total -= (sub_total * self.product_discount / 100)

        gst_amount = sub_total * self.gst / 100
        grand_total = sub_total + gst_amount

        self.stone_price = total_stone_price
        self.sub_total = sub_total
        self.gst = self.gst
        self.grand_total = grand_total
        self.gross_weight = self.metal_weight + (total_stone_weight * 0.2)

        self.save()

        return {
            "metal_price": metal_price,
            "stone_details": stone_details,
            "making_charge_after_discount": making_charge_price,
            "sub_total": sub_total,
            "gst": gst_amount,
            "grand_total": grand_total,
            "gross_weight": self.gross_weight
        }
    
    def __str__(self):
        return self.head

    @property
    def stone_names(self):
        return [ps.stone.name for ps in self.productstone_set.all()]

   


class ProductStone(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stone = models.ForeignKey(Stone, on_delete=models.CASCADE)
    count = models.IntegerField()
    weight = models.FloatField(help_text="Weight of one stone in carat")

    def get_formatted_single_stone_weight(self):
        gram = self.weight * 0.2
        return f"1 stone: {self.weight:.3f} ct / {gram:.3f} g"

    def __str__(self):
        return f"{self.product.head} - {self.stone.name}"
