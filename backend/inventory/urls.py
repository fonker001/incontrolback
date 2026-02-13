from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView,
    ProductStockValuationAPIView,
    ProductQuickSearchAPIView,
    InventoryLogListCreateAPIView,
    InventoryLogDetailAPIView,
)

urlpatterns = [
    # Categories
    path('categories/', CategoryListCreateAPIView.as_view()),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view()),

    # Products
    path('products/', ProductListCreateAPIView.as_view()),
    path('products/<int:pk>/', ProductDetailAPIView.as_view()),
    path('products/stock-valuation/', ProductStockValuationAPIView.as_view()),
    path('products/quick-search/', ProductQuickSearchAPIView.as_view()),

    # Inventory (Stock-In)
    path('stock-in/', InventoryLogListCreateAPIView.as_view()),
    path('stock-in/<int:pk>/', InventoryLogDetailAPIView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
