from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, filters
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, DecimalField
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from .models import Category, Product, InventoryLog
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    InventoryLogSerializer,
)
from rest_framework.permissions import AllowAny, IsAuthenticated

class CategoryListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]
    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    def put(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        serializer = CategorySerializer(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        category = get_object_or_404(Category, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'is_active', 'brand_name']
    search_fields = ['brand_name', 'product_name']
    ordering_fields = ['selling_price', 'created_at', 'stock_qty']

    def get(self, request):
        queryset = Product.objects.all()

        # Manually apply filters APIView does NOT auto-run them
        for backend in self.filter_backends:
            queryset = backend().filter_queryset(request, queryset, self)

        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductStockValuationAPIView(APIView):
    def get(self, request):
        stats = Product.objects.aggregate(
            total_stock_items=Sum('stock_qty'),
            potential_revenue=Sum(
                F('stock_qty') * F('selling_price'),
                output_field=DecimalField()
            )
        )

        return Response({
            "total_items_in_warehouse": stats['total_stock_items'] or 0,
            "total_potential_revenue": stats['potential_revenue'] or 0.00,
            "message": "This represents the total retail value of your current inventory."
        })


class ProductQuickSearchAPIView(APIView):
    def get(self, request):
        brand = request.query_params.get('brand')
        queryset = Product.objects.all()

        if brand:
            queryset = queryset.filter(brand_name__icontains=brand)

        data = queryset.values(
            'id',
            'brand_name',
            'product_name',
            'description',
            'selling_price',
        )

        return Response(data)


class InventoryLogListCreateAPIView(APIView):
    def get(self, request):
        logs = InventoryLog.objects.all().order_by('-delivery_date')
        serializer = InventoryLogSerializer(logs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = InventoryLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InventoryLogDetailAPIView(APIView):
    def get(self, request, pk):
        log = get_object_or_404(InventoryLog, pk=pk)
        serializer = InventoryLogSerializer(log)
        return Response(serializer.data)

    def delete(self, request, pk):
        log = get_object_or_404(InventoryLog, pk=pk)
        log.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
