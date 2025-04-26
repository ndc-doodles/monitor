from django.shortcuts import render,  get_object_or_404
from . models import*
from django.contrib.auth import logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password
# Create your views here.
from django.db.models import Q

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
class ProductListCreateAPIView(BaseListCreateAPIView):
    model = Product
    serializer_class = ProductSerializer

class ProductDetailAPIView(BaseDetailAPIView):
    model = Product
    serializer_class = ProductSerializer

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