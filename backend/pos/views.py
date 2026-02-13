from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import POSSale
from .serializers import POSSaleSerializer

class POSSaleViewSet(viewsets.ModelViewSet):
    """
    Handles physical walk-in sales.
    """
    queryset = POSSale.objects.all().order_by('-timestamp')
    serializer_class = POSSaleSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)