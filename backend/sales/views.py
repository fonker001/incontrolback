from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Sale, SaleItem
from .serializers import SaleSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().prefetch_related('items', 'client')
    serializer_class = SaleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    
    filterset_fields = ['status', 'client']
    search_fields = ['transaction_id', 'client__first_name', 'client__last_name']
    ordering_fields = ['sale_date', 'total_amount']

    def create(self, request, *args, **kwargs):
        """
        Custom create to handle the complex logic of adding 
        multiple SaleItems in one request from Next.js.
        """
        items_data = request.data.pop('items', [])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        sale = serializer.save()

        # Create the individual items
        for item in items_data:
            SaleItem.objects.create(sale=sale, **item)
        
        # Refresh to get the updated total_amount from signals
        sale.refresh_from_db()
        return Response(self.get_serializer(sale).data, status=status.HTTP_201_CREATED)