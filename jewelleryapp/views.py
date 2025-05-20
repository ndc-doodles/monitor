from rest_framework import generics
from django.shortcuts import render,  get_object_or_404
from . models import*
from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
# Create your views here.
from django.db.models import Q
from rest_framework.exceptions import NotFound
from django.conf import settings
from rest_framework.generics import ListAPIView
from urllib.parse import urljoin
from rest_framework.parsers import MultiPartParser, FormParser
from cloudinary.uploader import upload
import requests
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated  

from django.conf import settings
from django.views import View

from django.http import Http404
from .serializers import *
import cloudinary
import cloudinary.uploader
from rest_framework.filters import BaseFilterBackend
from rest_framework import status, permissions
import json
from rest_framework import generics

from rest_framework.response import Response
from rest_framework import status

# class GoogleLogin(SocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
#     client_class = OAuth2Client


# class GoogleLoginCallback(APIView):
#     def get(self, request, *args, **kwargs):
#         """
#         If you are building a fullstack application (eq. with React app next to Django)
#         you can place this endpoint in your frontend application to receive
#         the JWT tokens there - and store them in the state
#         """

#         code = request.GET.get("code")

#         if code is None:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
        
#         # Remember to replace the localhost:8000 with the actual domain name before deployment
#         token_endpoint_url = urljoin("http://localhost:8000/", reverse("google_login"))
#         response = requests.post(url=token_endpoint_url, data={"code": code})

#         return Response(response.json(), status=status.HTTP_200_OK)
    
# class LoginPage(View):
#     def get(self, request, *args, **kwargs):
       
#         return render(
#             request,
#             "login.html",
#             {
#                 "google_callback_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
#                 "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
                
#             },
            
#         )
    

def index(request):
    return render(request, 'index.html')

class BaseListCreateAPIView(APIView):
    model = None
    serializer_class = None

    def get(self, request):
        items = self.model.objects.all()
        serializer = self.serializer_class(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        image = request.FILES.get('image')

        if image:
            cloudinary_response = cloudinary.uploader.upload(image)
            public_id = cloudinary_response.get('public_id')
            if public_id:
                data['image'] = public_id

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseDetailAPIView(APIView):
    model = None
    serializer_class = None

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk)

    def get(self, request, pk):
        obj = self.get_object(pk)
        serializer = self.serializer_class(obj)
        return Response(serializer.data)

    def put(self, request, pk):
        instance = self.get_object(pk)
        data = request.data.copy()
        image = request.FILES.get('image')

        if image:
            cloudinary_response = cloudinary.uploader.upload(image)
            public_id = cloudinary_response.get('public_id')
            if public_id:
                data['image'] = public_id

        serializer = self.serializer_class(instance, data=data, partial = True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        obj = self.get_object(pk)
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductListCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        image_urls = []

        try:
            for image in images[:5]:  # Limit upload to 5 images max
                upload_result = uploader.upload(image)
                image_urls.append(upload_result["secure_url"])
        except Exception as e:
            return Response({"error": f"Image upload failed: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        data = request.data.copy()
        data['images'] = image_urls

        if 'ar_model_glb' in request.FILES:
            glb_upload = uploader.upload(request.FILES['ar_model_glb'], resource_type='raw')
            cloud_name = 'dvllntzo0'
            public_id = glb_upload['public_id']
            version = glb_upload['version']
            data['ar_model_glb'] = f"https://res.cloudinary.com/{cloud_name}/raw/upload/v{version}/{public_id}"

        if 'ar_model_gltf' in request.FILES:
            gltf_upload = uploader.upload(request.FILES['ar_model_gltf'], resource_type='raw')
            data['ar_model_gltf'] = gltf_upload['secure_url']  # Use secure_url here for consistency

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        classic_products = Product.objects.filter(is_classic=True)
        other_products = Product.objects.filter(is_classic=False)

        classic_data = ProductSerializer(classic_products, many=True).data
        other_data = ProductSerializer(other_products, many=True).data

        return Response({
            "classic_products": classic_data,
            "other_products": other_data
        }, status=status.HTTP_200_OK)



class ProductDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound("Product not found")

    def get(self, request, pk, *args, **kwargs):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        product = self.get_object(pk)
        data = dict(request.data)

        new_images = request.FILES.getlist('images')
        if new_images:
            uploaded_images = []
            try:
                for image in new_images[:5]:
                    upload_result = uploader.upload(image)
                    uploaded_images.append(upload_result["secure_url"])
                data['images'] = json.dumps(uploaded_images)  # convert to JSON string
            except Exception as e:
                return Response(
                    {"error": f"Image upload failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            data.pop('images', None)

        if 'ar_model_glb' in request.FILES:
            glb_upload = uploader.upload(request.FILES['ar_model_glb'], resource_type='raw')
            cloud_name = 'dvllntzo0'
            public_id = glb_upload['public_id']
            version = glb_upload['version']
            data['ar_model_glb'] = f"https://res.cloudinary.com/{cloud_name}/raw/upload/v{version}/{public_id}"

        if 'ar_model_gltf' in request.FILES:
            gltf_upload = uploader.upload(request.FILES['ar_model_gltf'], resource_type='raw')
            data['ar_model_gltf'] = gltf_upload['secure_url']

        # ✅ Deserialize JSON string before validation
        if 'images' in data and isinstance(data['images'], str):
            try:
                data['images'] = json.loads(data['images'])  # convert back to Python list
            except json.JSONDecodeError:
                return Response({"images": ["Value must be valid JSON."]}, status=400)

        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ProductDetailAPIView(APIView):
#     def put(self, request, pk, *args, **kwargs):
#         try:
#             product = Product.objects.get(pk=pk)
#         except Product.DoesNotExist:
#             return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

#         data = request.data.copy()

#         # Convert images string to list if needed
#         images = data.get('images')
#         if images and isinstance(images, str):
#             try:
#                 data['images'] = json.loads(images)
#             except json.JSONDecodeError:
#                 return Response({"images": ["Value must be valid JSON."]}, status=400)

#         serializer = ProductSerializer(product, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=400)
class ProductListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(is_classic=False)
        serializer = ProductSerializer(products, many=True)
        return Response({
            "products": serializer.data
        }, status=status.HTTP_200_OK)

class ClassicProductListAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')  # Optional

        # Try to get user only if user_id is provided
        user = None
        if user_id:
            if not user_id.isdigit():
                return Response({"error": "Invalid user_id. Must be a number."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = Register.objects.get(id=int(user_id))
            except Register.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Fetch classic products
        products = Product.objects.filter(is_classic=True)
        serializer = ClassicProductListSerializer(products, many=True)
        products_data = serializer.data

        # If user is found, check wishlist products
        wishlist_product_ids = set()
        if user:
            wishlist_product_ids = set(
                Wishlist.objects.filter(user=user).values_list('product_id', flat=True)
            )

        # Add detail_url and wishlist status
        for product in products_data:
            product_id = product["id"]
            product['detail_url'] = request.build_absolute_uri(f'/api/products/classic/{product_id}/')
            product['wishlist'] = product_id in wishlist_product_ids

        return Response({
            "classic_products": products_data
        }, status=status.HTTP_200_OK)

class ClassicProductDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk, is_classic=True)
        except Product.DoesNotExist:
            raise NotFound("Classic product not found")

    # ✅ POST: Create a new classic product
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data['is_classic'] = True  # Force it to be a classic product

        new_images = request.FILES.getlist('images')
        if new_images:
            uploaded_images = []
            try:
                for image in new_images[:5]:  # Limit to 5
                    upload_result = uploader.upload(image)
                    uploaded_images.append(upload_result['secure_url'])
                data['images'] = uploaded_images
            except Exception as e:
                return Response({"error": f"Image upload failed: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if 'ar_model_glb' in request.FILES:
            glb_upload = uploader.upload(request.FILES['ar_model_glb'], resource_type='raw')
            version = glb_upload['version']
            public_id = glb_upload['public_id']
            cloud_name = 'dvllntzo0'
            data['ar_model_glb'] = f"https://res.cloudinary.com/{cloud_name}/raw/upload/v{version}/{public_id}"

        if 'ar_model_gltf' in request.FILES:
            gltf_upload = uploader.upload(request.FILES['ar_model_gltf'], resource_type='raw')
            data['ar_model_gltf'] = gltf_upload['secure_url']

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✅ GET: Get classic product by ID
    def get(self, request, pk, *args, **kwargs):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    # ✅ PUT: Update classic product
    def put(self, request, pk, *args, **kwargs):
        product = self.get_object(pk)
        data = request.data.copy()

        new_images = request.FILES.getlist('images')
        if new_images:
            uploaded_images = []
            try:
                for image in new_images[:5]:
                    upload_result = uploader.upload(image)
                    uploaded_images.append(upload_result['secure_url'])
                data['images'] = uploaded_images
            except Exception as e:
                return Response(
                    {"error": f"Image upload failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            data.pop('images', None)

        if 'ar_model_glb' in request.FILES:
            glb_upload = uploader.upload(request.FILES['ar_model_glb'], resource_type='raw')
            version = glb_upload['version']
            public_id = glb_upload['public_id']
            cloud_name = 'dvllntzo0'
            data['ar_model_glb'] = f"https://res.cloudinary.com/{cloud_name}/raw/upload/v{version}/{public_id}"

        if 'ar_model_gltf' in request.FILES:
            gltf_upload = uploader.upload(request.FILES['ar_model_gltf'], resource_type='raw')
            data['ar_model_gltf'] = gltf_upload['secure_url']

        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✅ DELETE: Delete classic product
    def delete(self, request, pk, *args, **kwargs):
        product = self.get_object(pk)
        product.delete()
        return Response({"detail": "Classic product deleted."}, status=status.HTTP_204_NO_CONTENT)

    

# Material API
class MaterialListCreateAPIView(BaseListCreateAPIView):
    model = Material
    serializer_class = MaterialSerializer

class MaterialDetailAPIView(BaseDetailAPIView):
    model = Material
    serializer_class = MaterialSerializer

# Category API
class CategoryListCreateAPIView(BaseListCreateAPIView):                                          
    model = Category
    serializer_class = CategorySerializer

class CategoryDetailAPIView(BaseDetailAPIView):
    model = Category
    serializer_class = CategorySerializer

class SevenCategoriesAPIView(APIView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.order_by('?')[:7]
        serializer = CategorySerializer(categories, many=True)
        return Response({
            "categories": serializer.data
        }, status=status.HTTP_200_OK)


# Metal API
class MetalListCreateAPIView(BaseListCreateAPIView):
    model = Metal
    serializer_class = MetalSerializer

class MetalDetailAPIView(BaseDetailAPIView):
    model = Metal
    serializer_class = MetalSerializer

# Stone API
class StoneListCreateAPIView(BaseListCreateAPIView):
    model = Gemstone
    serializer_class = StoneSerializer

class StoneDetailAPIView(BaseDetailAPIView):
    model = Gemstone
    serializer_class = StoneSerializer

class NavbarCategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = NavbarCategory.objects.all().order_by('order')
    serializer_class = NavbarCategorySerializer

class NavbarCategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NavbarCategory.objects.all()
    serializer_class = NavbarCategorySerializer
    lookup_field = 'pk'


# Occasion API
class OccasionListCreateAPIView(BaseListCreateAPIView):
    model = Occasion
    serializer_class = OccasionSerializer

class OccasionDetailAPIView(BaseDetailAPIView):
    model = Occasion
    serializer_class = OccasionSerializer

# Gender API
class GenderListCreateAPIView(BaseListCreateAPIView):
    model = Gender
    serializer_class = GenderSerializer

class GenderDetailAPIView(BaseDetailAPIView):
    model = Gender
    serializer_class = GenderSerializer

class ContactListCreateAPIView(BaseListCreateAPIView):
    model = Contact
    serializer_class = ContactSerializer

class ContactDetailAPIView(BaseDetailAPIView):
    model = Contact
    serializer_class = ContactSerializer
    
class ProductFilterAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()

        # Retrieve query parameters from the request
        category = self.request.query_params.get('category')
        metal = self.request.query_params.get('metal')
        material = self.request.query_params.get('material')
        occasion = self.request.query_params.get('occasion')
        gender = self.request.query_params.get('gender')
        price_min = self.request.query_params.get('price_min')
        price_max = self.request.query_params.get('price_max')
        stone = self.request.query_params.get('stone')
        is_handcrafted = self.request.query_params.get('is_handcrafted')

        # Apply filters based on the query parameters
        if category:
            queryset = queryset.filter(category__name__iexact=category)
        if metal:
            queryset = queryset.filter(metal__name__iexact=metal)
        if material:
            queryset = queryset.filter(metal__material__name__iexact=material)
        if occasion:
            queryset = queryset.filter(occasions__name__iexact=occasion)
        if gender:
            queryset = queryset.filter(gender__name__iexact=gender)
        if price_min:
            queryset = queryset.filter(grand_total__gte=price_min)
        if price_max:
            queryset = queryset.filter(grand_total__lte=price_max)
        if stone:
            queryset = queryset.filter(productstone__stone__name__iexact=stone)
        if is_handcrafted is not None:
            if is_handcrafted.lower() == 'true':
                queryset = queryset.filter(is_handcrafted=True)
            elif is_handcrafted.lower() == 'false':
                queryset = queryset.filter(is_handcrafted=False)

       
        # Return distinct products based on the applied filters
        return queryset.distinct()
    


class ProductSearchAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        is_handcrafted = self.request.query_params.get('is_handcrafted', None)

        if query:
            queryset = Product.objects.filter(
                Q(head__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(metal__name__icontains=query) |
                Q(metal__material__name__icontains=query) |
                Q(gender__name__icontains=query) |
                Q(occasion__name__icontains=query) |  # fixed field name here
                Q(stones__name__icontains=query)
            ).distinct()
        else:
            queryset = Product.objects.all()

        # Apply handcrafted filter if provided
        if is_handcrafted is not None:
            if is_handcrafted.lower() == 'true':
                queryset = queryset.filter(is_handcrafted=True)
            elif is_handcrafted.lower() == 'false':
                queryset = queryset.filter(is_handcrafted=False)

        return queryset
    
    
class ProductShareAPIView(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product_url = request.build_absolute_uri(f'/product/{product.pk}/')  # Adjust path if needed
        share_text = f"Check out this product: {product.head}"

        share_links = {
            "whatsapp": f"https://wa.me/?text={share_text} {product_url}",
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={product_url}",
            "telegram": f"https://t.me/share/url?url={product_url}&text={share_text}",
            "instagram": "https://www.instagram.com/"  # Cannot share directly, provide profile or app link
        }

        return Response({
            "product_id": product.pk,
            "product_head": product.head,
            "product_url": product_url,
            "share_links": share_links
        }, status=status.HTTP_200_OK)
    

class ProductStoneListCreateAPIView(generics.ListCreateAPIView):
    queryset = ProductStone.objects.all()
    serializer_class = ProductStoneSerializer


class ProductStoneDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductStone.objects.all()
    serializer_class = ProductStoneSerializer

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        # Create the serializer instance with the request data
        serializer = RegisterSerializer(data=request.data)
        
        # Check if the serializer is valid
        if serializer.is_valid():
            # Save the data (create the user) if valid
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        
        # Return validation errors if the data is not valid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserProfileCreateView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def perform_create(self, serializer):
        # Get the user (Register model) ID from the request data
        user_id = self.request.data.get('user') # Get the 'user' field from the request body (which should be an ID)
        user_id = int(user_id)
        print("sangu mon",type(user_id))
        # Fetch the Register instance using the provided user ID
        user = get_object_or_404(Register, id=user_id)
        print('the user is',user)
        username = user.username
        
        # Save the UserProfile with the user (Register model)
        serializer.save(user=username)

class UserProfileUpdateView(generics.UpdateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def get_object(self):
        # Get the UserProfile instance by ID from the URL
        obj = UserProfile.objects.get(id=self.kwargs["id"])
        return obj



class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # Check if the user exists
            try:
                user = Register.objects.get(username=username)
                # Manually check the password hash
                if check_password(password, user.password):  # Use check_password to validate hashed password
                    # Generate JWT tokens on successful authentication
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    })
                else:
                    return Response({"detail": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)
            except Register.DoesNotExist:
                return Response({"detail": "Invalid username."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LogoutAPIView(APIView):
    def post(self, request):
        # Call Django's built-in logout function to clear the session
        logout(request)
        
        # Return a success response
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
   
User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class WishlistAPIView(APIView):
    # ✅ GET all wishlist items for a user
    def get(self, request):
        user_id = request.query_params.get("user_id")
        if not user_id:
            return Response({"error": "user_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = int(user_id)  # Validate and sanitize input
            user = Register.objects.get(id=user_id)
        except ValueError:
            return Response({"error": "Invalid user_id. Must be a number."}, status=status.HTTP_400_BAD_REQUEST)
        except Register.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        wishlist = Wishlist.objects.filter(user=user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ✅ POST (Add product to wishlist)
    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data.get('user_id')  # This will be a Register object due to serializer
            product = serializer.validated_data.get('product')

            wishlist_item, created = Wishlist.objects.get_or_create(user=user, product=product)

            if created:
                return Response({"message": "Product added to wishlist"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"message": "Product already in wishlist"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ✅ DELETE wishlist item
    def delete(self, request, wishlist_id):
        try:
            wishlist_item = Wishlist.objects.get(id=wishlist_id)
            wishlist_item.delete()
            return Response({"message": "Removed from wishlist"}, status=status.HTTP_204_NO_CONTENT)
        except Wishlist.DoesNotExist:
            return Response({"error": "Wishlist item not found"}, status=status.HTTP_404_NOT_FOUND)

class UserLoginView(APIView):
    permission_classes = []  # No authentication required for login

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Please provide both username and password"}, status=status.HTTP_400_BAD_REQUEST)

        # Authenticate securely
        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "User account is disabled"}, status=status.HTTP_403_FORBIDDEN)

        # Identify user type
        user_type = "customer"
        if user.is_superuser:
            user_type = "superuser"

        # Generate JWT tokens manually
        tokens = get_tokens_for_user(user)

        response_data = {
            "message": "Login successful",
            "access_token": tokens["access"],
            "refresh_token": tokens["refresh"],
            "username": user.username,
            "user_type": user_type,
        }

        return Response(response_data, status=status.HTTP_200_OK) 
    

class RecommendProductsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        username = request.query_params.get('username')

        # Step 1: Try to fetch user visits if username is provided
        if username:
            try:
                user = Register.objects.get(username=username)
                visits = UserVisit.objects.filter(user=user).order_by('-timestamp')[:5]
                visited_products = Product.objects.filter(id__in=visits.values_list('product_id', flat=True))

                if visited_products.exists():
                    serializer = ProductSerializer(visited_products, many=True)
                    return Response({
                        "type": "related",
                        "products": serializer.data
                    }, status=status.HTTP_200_OK)

            except Register.DoesNotExist:
                pass  # If user doesn't exist, proceed to random category fallback

        # Step 2: Fallback - pick a random category that has products
        categories_with_products = Category.objects.filter(product__isnull=False).distinct()

        if categories_with_products.exists():
            for category in categories_with_products.order_by('?'):
                products = Product.objects.filter(category=category)[:5]
                if products.exists():
                    serializer = ProductSerializer(products, many=True)
                    return Response({
                        "type": "random_category",
                        "category": category.name,
                        "products": serializer.data
                    }, status=status.HTTP_200_OK)

        # Step 3: Final fallback - get any products if nothing above works
        fallback_products = Product.objects.all()[:5]
        if fallback_products.exists():
            serializer = ProductSerializer(fallback_products, many=True)
            return Response({
                "type": "fallback_all",
                "products": serializer.data
            }, status=status.HTTP_200_OK)

        # Step 4: No products at all
        return Response({
            "message": "No products found"
        }, status=status.HTTP_404_NOT_FOUND)
    

class HeaderListCreateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        slider_images = request.FILES.getlist('slider_images')
        main_imgs = request.FILES.getlist('main_img')
        main_mobile_imgs = request.FILES.getlist('main_mobile_img')

        uploaded_slider_images = []
        uploaded_main_imgs = []
        uploaded_main_mobile_imgs = []

        for img in slider_images:
            uploaded_slider_images.append(upload(img)['url'])

        for img in main_imgs:
            uploaded_main_imgs.append(upload(img)['url'])

        for img in main_mobile_imgs:
            uploaded_main_mobile_imgs.append(upload(img)['url'])

        header = Header.objects.create(
            slider_images=uploaded_slider_images,
            main_img=uploaded_main_imgs,
            main_mobile_img=uploaded_main_mobile_imgs
        )
        serializer = HeaderSerializer(header)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        headers = Header.objects.all()
        serializer = HeaderSerializer(headers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class HeaderDetailAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request, pk, *args, **kwargs):
        try:
            header = Header.objects.get(pk=pk)
        except Header.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = HeaderSerializer(header)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        try:
            header = Header.objects.get(pk=pk)
        except Header.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        slider_images = request.FILES.getlist('slider_images')
        main_imgs = request.FILES.getlist('main_img')
        main_mobile_imgs = request.FILES.getlist('main_mobile_img')

        uploaded_slider_images = []
        uploaded_main_imgs = []
        uploaded_main_mobile_imgs = []

        for img in slider_images:
            uploaded_slider_images.append(upload(img)['url'])

        for img in main_imgs:
            uploaded_main_imgs.append(upload(img)['url'])

        for img in main_mobile_imgs:
            uploaded_main_mobile_imgs.append(upload(img)['url'])

        header.slider_images = uploaded_slider_images
        header.main_img = uploaded_main_imgs
        header.main_mobile_img = uploaded_main_mobile_imgs
        header.save()

        serializer = HeaderSerializer(header)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        try:
            header = Header.objects.get(pk=pk)
        except Header.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        header.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class RecentProductsWithFallbackAPIView(ListAPIView):
    serializer_class = RecentProductSerializer

    def get_queryset(self):
        limit = int(self.request.query_params.get('limit', 20))
        days = int(self.request.query_params.get('days', 15))
        cutoff_date = timezone.now() - timedelta(days=days)

        recent_qs = Product.objects.filter(created_at__gte=cutoff_date).order_by('-id')[:limit]
        if recent_qs.exists():
            self.from_fallback = False
            return recent_qs
        fallback_qs = Product.objects.all().order_by('-id')[:limit]
        self.from_fallback = True
        return fallback_qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "from_fallback": self.from_fallback,
            "count": len(serializer.data),
            "products": serializer.data
        })

    

class ProductListByGender(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        gender_id = self.request.query_params.get('gender')
        if gender_id:
            return Product.objects.filter(gender_id=gender_id)
        return Product.objects.all()
    
# class SevenCategoriesAPIView(APIView):
#     def get(self, request, *args, **kwargs):
#         categories = Category.objects.order_by('?')[:7]  # Get 7 random categories
#         serializer = CategorySerializer(categories, many=True)
#         return Response({
#             "categories": serializer.data
#         },status=status.HTTP_200_OK)


class SevenCategoriesAPIView(APIView):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.order_by('?')[:7]  # 7 random categories
        serializer = CategorySerializer(categories, many=True)
        return Response({"categories": serializer.data}, status=status.HTTP_200_OK)

class CategoryDetailAPIView(APIView):
    def get(self, request, pk, *args, **kwargs):
        category = get_object_or_404(Category, pk=pk)
        products = Product.objects.filter(category=category)
        serializer = FinestProductSerializer(products, many=True)
        return Response({
            "category": category.name,
            "products": serializer.data
        }, status=status.HTTP_200_OK)
    
class RelatedProductsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get('product_id')

        if not product_id:
            return Response({"error": "product_id query param is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        # Get related products in the same category but exclude the current product
        related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:10]

        serializer = ProductSerializer(related_products, many=True)
        return Response({"related_products": serializer.data}, status=status.HTTP_200_OK)
    
class ProductRatingAPIView(APIView):

    def post(self, request):
        serializer = ProductRatingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        if pk:
            rating = get_object_or_404(ProductRating, pk=pk)
            serializer = ProductRatingSerializer(rating)
            return Response(serializer.data)
        else:
            ratings = ProductRating.objects.all()
            serializer = ProductRatingSerializer(ratings, many=True)
            return Response(serializer.data)

    def put(self, request, pk):
        rating = get_object_or_404(ProductRating, pk=pk)
        serializer = ProductRatingSerializer(rating, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)