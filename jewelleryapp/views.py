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

import requests
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

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
        # Handle image upload
        images = request.FILES.getlist('image')  # Ensure it's a list of files
        image_urls = []

        try:
            for image in images[:5]:  # Limit to 5 images
                upload_result = cloudinary.uploader.upload(image)
                image_urls.append(upload_result["secure_url"])
        except Exception as e:
            return Response({"error": f"Image upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Combine original request data with uploaded image URLs
        data = request.data.copy()
        data['images'] = image_urls  # 'images' must match your model field

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request, *args, **kwargs):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class ProductDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise NotFound(detail="Product not found")

    def put(self, request, pk, *args, **kwargs):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        new_images = request.FILES.getlist('images')
        uploaded_images = []

        if new_images:
            try:
                for image in new_images[:5]:
                    upload_result = cloudinary.uploader.upload(image)
                    uploaded_images.append(upload_result["secure_url"])
            except Exception as e:
                return Response({"error": f"Image upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            existing_images = product.images if product.images else []
            all_images = uploaded_images + existing_images
            data['images'] = json.dumps(all_images[:5])  # Ensure valid JSON string

        # Don't include 'images' in data if no new uploads and you want to leave existing images untouched
        elif 'images' in data:
            data.pop('images')  # Remove if user sent empty key

        # Use serializer to update other fields too
        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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

# Metal API
class MetalListCreateAPIView(BaseListCreateAPIView):
    model = Metal
    serializer_class = MetalSerializer

class MetalDetailAPIView(BaseDetailAPIView):
    model = Metal
    serializer_class = MetalSerializer

# Stone API
class StoneListCreateAPIView(BaseListCreateAPIView):
    model = Stone
    serializer_class = StoneSerializer

class StoneDetailAPIView(BaseDetailAPIView):
    model = Stone
    serializer_class = StoneSerializer

# Product API






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

       
        # Return distinct products based on the applied filters
        return queryset.distinct()
    


class ProductSearchAPIView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query:
            return Product.objects.filter(
                Q(head__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query) |
                Q(metal__name__icontains=query) |
                Q(metal__material__name__icontains=query) |
                Q(gender__name__icontains=query) |
                Q(occasions__name__icontains=query) |
                Q(stones__name__icontains=query)  # 🔥 added search in stone names
            ).distinct()
        return Product.objects.none()
    

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
   
class WishlistAPIView(APIView):
    # ✅ GET all wishlist items for a user
    def get(self, request, user_id):
        try:
            user = Register.objects.get(id=user_id)
            wishlist = Wishlist.objects.filter(user=user)
            serializer = WishlistSerializer(wishlist, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Register.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ POST (Add product to wishlist)
    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data.get('user_id').id
            product = serializer.validated_data.get('product')

            user = Register.objects.get(id=user_id)
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
        


User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

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
        username = request.query_params.get('username', None)

        if username:
            try:
                user = Register.objects.get(username=username)
                visits = UserVisit.objects.filter(user=user).order_by('-timestamp')[:5]
                visited_products = Product.objects.filter(id__in=visits.values_list('product_id', flat=True))
                if visited_products.exists():
                    serializer = ProductSerializer(visited_products, many=True)
                    return Response({"type": "related", "products": serializer.data})
            except Register.DoesNotExist:
                pass  # If user not found, treat as new user

        # New visitor or username not provided
        random_category = Category.objects.order_by('?').first()
        if random_category:
            products = Product.objects.filter(category=random_category)[:5]
            serializer = ProductSerializer(products, many=True)
            return Response({"type": "random_category", "category": random_category.name, "products": serializer.data})

        return Response({"message": "No products found"})