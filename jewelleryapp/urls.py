

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
    path('api/gemstone/', StoneListCreateAPIView.as_view()),
    path('api/gemstone/<int:pk>/', StoneDetailAPIView.as_view()),

    path('api/materials/', MaterialListCreateAPIView.as_view()),
    path('api/materials/<int:pk>/', MaterialDetailAPIView.as_view()),

    #product
    path('api/products/', ProductListCreateAPIView.as_view(), name='product-list-create'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='product-detail'),

    path('api/occasions/', OccasionListCreateAPIView.as_view()),
    path('api/occasions/<int:pk>/', OccasionDetailAPIView.as_view()),

    path('api/contact/', ContactListCreateAPIView.as_view()),
    path('api/contact/<int:pk>/', ContactDetailAPIView.as_view()),

    path('api/genders/', GenderListCreateAPIView.as_view()),
    path('api/genders/<int:pk>/', GenderDetailAPIView.as_view()),

    path('api/products/filter/', views.ProductFilterAPIView.as_view(), name='product-filter'),
    path('api/products/search/', ProductSearchAPIView.as_view(), name='product-search'),
    path('api/products/<int:pk>/share/', ProductShareAPIView.as_view(), name='product-share'), 
    path('api/products/recommend/', RecommendProductsAPIView.as_view(), name='product-recommend'),
    
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

    path('api/product-stones/', views.ProductStoneListCreateAPIView.as_view(), name='productstone-list-create'),
    path('api/product-stones/<int:pk>/', views.ProductStoneDetailAPIView.as_view(), name='productstone-detail'),
    path('api/products/recent-with-fallback/', RecentProductsWithFallbackAPIView.as_view(), name='recent-products-fallback'),
    path('api/products/by-gender/', ProductListByGender.as_view(), name='product-list-by-gender'),
    path('api/products/non-classic/', ProductListAPIView.as_view(), name='product-non-classic'),  # GET non-classic only
    path('api/products/classic/', ClassicProductListAPIView.as_view(), name='product-classic'),  # GET classic only
    path('api/products/classic/<int:pk>/', ClassicProductDetailAPIView.as_view(), name='product-classic-detail'),
    path('api/categories/seven/', SevenCategoriesAPIView.as_view(), name='seven-categories'),
    path('api/categories/seven/<int:pk>/', SevenCategoryDetailAPIView.as_view(), name='category-detail'),
    path('api/products/related/', RelatedProductsAPIView.as_view(), name='related-products'),
    path('api/ratings/', ProductRatingAPIView.as_view(), name='rating-list-create'),        # POST, GET all
    path('api/ratings/<int:pk>/', ProductRatingAPIView.as_view(), name='rating-detail'),
    path('api/navbar-categories/', NavbarCategoryListCreateAPIView.as_view(), name='navbarcategory-list-create'),
    path('api/navbar-categories/<int:pk>/', NavbarCategoryRetrieveUpdateDestroyAPIView.as_view(), name='navbarcategory-detail'),
] 