from rest_framework import serializers 
from models import Invoice
from Patient.models import Patient

class InvoiceSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    
    class Meta:
        model = Invoice
        fields = [
            "service",
            "cost",
            "patient_id",
        ]