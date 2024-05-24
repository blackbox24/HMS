from rest_framework import serializers
from .models import Doctor
from Department.models import Department

class DoctorSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())

    class Meta:
        model = Doctor
        fields = [
            'doctor_fname',
            'doctor_lname',
            'doctor_phone',
            'department_id'
        ]
