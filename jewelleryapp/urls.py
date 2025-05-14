

from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', views.index),
    path('api/categories/', CategoryListCreateAPIView.as_view()),
    path('api/categories/<int:pk>/', CategoryDetailAPIView.as_view()),

    # Metal
    path('api/metals/', MetalListCreateAPIView.as_view()),
    path('api/metals/<int:pk>/', MetalDetailAPIView.as_view()),

    # Stone
    path('api/stones/', StoneListCreateAPIView.as_view()),
    path('api/stones/<int:pk>/', StoneDetailAPIView.as_view()),

    path('api/materials/', MaterialListCreateAPIView.as_view()),
    path('api/materials/<int:pk>/', MaterialDetailAPIView.as_view()),

    #product
    path('api/products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),

    path('api/occasions/', OccasionListCreateAPIView.as_view()),
    path('api/occasions/<int:pk>/', OccasionDetailAPIView.as_view()),

    path('api/genders/', GenderListCreateAPIView.as_view()),
    path('api/genders/<int:pk>/', GenderDetailAPIView.as_view()),

    path('api/products/filter/', views.ProductFilterAPIView.as_view(), name='product-filter'),
    path('api/products/search/', ProductSearchAPIView.as_view(), name='product-search'),
    path('api/products/<int:pk>/share/', ProductShareAPIView.as_view(), name='product-share'), 
    path('api/products/`recommend`/', RecommendProductsAPIView.as_view(), name='product-recommend'),
    
    path('api/login/', LoginAPIView.as_view(), name='login'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),

    path('api/wishlist/<int:user_id>/', WishlistAPIView.as_view(), name='wishlist-list'),
    path('api/wishlist/', WishlistAPIView.as_view(), name='wishlist-add'),
    path('api/wishlist/delete/<int:wishlist_id>/', WishlistAPIView.as_view(), name='wishlist-delete'),

    path('api/userprofile/create/', UserProfileCreateView.as_view(), name='userprofile-create'),
    path('api/userprofile/update/<int:id>/', UserProfileUpdateView.as_view(), name='userprofile-update'),

    path('api/superuser-login/', UserLoginView.as_view(), name='api-superuser-login'),

    path('api/headers/', HeaderListCreateAPIView.as_view(), name='header-list-create'),  # POST for creating, GET for listing headers
    path('api/headers/<int:pk>/', HeaderDetailAPIView.as_view(), name='header-detail'),
]