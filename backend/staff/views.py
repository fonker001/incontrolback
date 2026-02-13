from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomAdmin, Supplier, Client
from .serializers import (
    SupplierSerializer, ClientSerializer,
    RequestOTPSerializer, VerifyOTPSerializer
)


class RequestOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomAdmin.objects.get(email=email, is_active=True)
                user.generate_otp()
                return Response({"message": "OTP sent to email."}, status=status.HTTP_200_OK)
            except CustomAdmin.DoesNotExist:
                return Response({"message": "If this email exists, an OTP has been sent."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            try:
                user = CustomAdmin.objects.get(email=email)
                if user.verify_otp(otp):
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': {
                            'email': user.email,
                            'full_name': f"{user.first_name} {user.last_name}"
                        }
                    }, status=status.HTTP_200_OK)
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_401_UNAUTHORIZED)
            except CustomAdmin.DoesNotExist:
                return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SupplierListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        suppliers = Supplier.objects.all()
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)


class SupplierCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupplierDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Supplier.objects.get(pk=pk)
        except Supplier.DoesNotExist:
            return None

    def get(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data)

    def put(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierSerializer(supplier, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        supplier = self.get_object(pk)
        if not supplier:
            return Response({"error": "Supplier not found."}, status=status.HTTP_404_NOT_FOUND)
        supplier.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ClientListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clients = Client.objects.all()
        serializer = ClientSerializer(clients, many=True)
        return Response(serializer.data)


class ClientCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ClientDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return None

    def get(self, request, pk):
        client = self.get_object(pk)
        if not client:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClientSerializer(client)
        return Response(serializer.data)

    def put(self, request, pk):
        client = self.get_object(pk)
        if not client:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClientSerializer(client, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        client = self.get_object(pk)
        if not client:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        client = self.get_object(pk)
        if not client:
            return Response({"error": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
        client.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
