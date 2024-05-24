from rest_framework import serializers
from .models import Pharmacy 

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = [
            "pharmacy_name",
            "pharmacy_address",
            "pharmacy_phone"
        ]