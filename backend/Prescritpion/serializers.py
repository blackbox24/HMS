from rest_framework import serializers
from models import Prescription
from Patient.models import Patient

class PrescriptionSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Prescription
        fields = [
            "patient_id",
            "medication",
            "expiry_date",
            "cost",
            "updated_at"
        ]

