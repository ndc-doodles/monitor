

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
]