from django.urls import path, include
from .views import *
from . import views
from .views import CombinedSuggestionsView
from rest_framework_simplejwt.views import TokenRefreshView
# gif_list = GifViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })

# gif_detail = GifViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })
# router = DefaultRouter()
# router.register(r'gifs', GifViewSet)

urlpatterns = [
    path('', views.index),
    path('api/categories/', CategoryListCreateAPIView.as_view()),
    path('api/categories/<int:pk>/', CategoryDetailAPIView.as_view()),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

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
    path('api/register/<uuid:id>/', RegisterDetailView.as_view()), 
    path('api/registerslist/', RegisterListView.as_view(), name='register-list'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),

    # path('api/wishlist/<int:user_id>/', WishlistAPIView.as_view(), name='wishlist-list'),
    # path('api/wishlist/', WishlistAPIView.as_view(), name='wishlist-add'),
    # path('api/wishlist/delete/<int:wishlist_id>/', WishlistAPIView.as_view(), name='wishlist-delete'),
    path('api/wishlist/', WishlistAPIView.as_view(), name='wishlist'),                      # List & add
    path('api/wishlist/<int:product_id>/', WishlistDetailAPIView.as_view(), name='wishlist-detail'),

    path('api/userprofiles/', UserProfileListView.as_view(), name='userprofile-list'),
    path('api/userprofile/create/', UserProfileCreateView.as_view(), name='userprofile-create'),
    path('api/userprofile/update/<int:id>/', UserProfileUpdateView.as_view(), name='userprofile-update'),
    path('api/profile/', UserProfileDetailView.as_view(), name='user-profile'),
    path('api/profile/image/', UserProfileImageUpdateView.as_view(), name='profile-image-update'),
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
    path('api/navbar-category-subdata/', NavbarCategorySubDataAPIView.as_view(), name='navbarcategory-subdata'),
    path('api/navbar-categories/mega/', NavbarCategoryListCreateAPIView.as_view(), name='navbar-categories-mega'),
    path('api/MegaNavbar/', MegaNavbar.as_view(), name='MegaNavbar'),

    # path('api/search-and-popular/', SearchAndPopularView.as_view(), name='search-and-popular'),
    # path('api/combined-suggestions/', CombinedSuggestionsView.as_view(), name='combined-suggestions'),
    # path('api/gif/', gif_list, name='gif-list'),
    # path('api/gif/<int:pk>/', gif_detail, name='gif-detail'),

    path('api/combined-suggestions/', CombinedSuggestionsView.as_view(), name='combined-suggestions'),
    path('api/combined-suggestions/?query=', CombinedSuggestionsView.as_view(), name='combined-suggestions'),
    path('api/gifs/', SearchGifAPIView.as_view()),          
    path('api/gifs/<int:pk>/', SearchGifAPIView.as_view()),

    path('api/send-otp/', SendOTP.as_view(), name='send-otp'),
    path('api/verify-otp/', VerifyOTP.as_view(), name='verify-otp'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/enquiry/<int:pk>/', ProductEnquiryAPIView.as_view(), name='product-enquiry'),
    path('api/enquiries/', ProductEnquiryListAPIView.as_view(), name='product-enquiry-list'),
] 