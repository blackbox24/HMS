from rest_framework import serializers
from Doctor.models import Doctor
from Patient.models import Patient
from .models import Appointment

class AppointmentSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = Appointment
        fields = [
            "patient_id",
            "doctor_id",
            "date",
        ]