from rest_framework import serializers
from models import Patient
from Pharmacy.models import Pharmacy

class PatientSerializer(serializers.ModelSerializer):
    pharmacy_id = serializers.PrimaryKeyRelatedField(queryset=Pharmacy.objects.all())
    class Meta:
        model = Patient
        fields = [
            'pharmacy_id',
            'patient_fname',
            'patient_lname',
            'patient_phone'
        ]

