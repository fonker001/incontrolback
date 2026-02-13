import re
from rest_framework import serializers
from .models import Supplier, Client

class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'email', 'phone_number', 
            'address', 'additional_info', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_phone_number(self, value):
        if value:
            value = value.replace(" ", "").replace("-", "")
            if not re.match(r"^\+?\d{9,15}$", value):
                raise serializers.ValidationError("Phone number must be between 9 and 15 digits.")
        return value

    def validate_additional_info(self, value):
        if value is not None and not isinstance(value, dict):
            raise serializers.ValidationError("Additional info must be a valid JSON object (dictionary).")
        return value


class ClientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 
            'email', 'phone_number', 'address', 
            'additional_info', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def validate_email(self, value):
        return value.lower() if value else value

    def validate(self, data):
        if not data.get('email') and not data.get('phone_number'):
            raise serializers.ValidationError(
                "A client must have at least an email address or a phone number."
            )
        return data