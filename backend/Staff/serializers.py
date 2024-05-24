from rest_framework import serializers
from .models import Staff
from Department.models import Department

class StaffSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    class Meta:
        model = Staff
        fields = [
            "department_id",
            "staff_fname",
            "staff_lname",
            "staff_address",
            "staff_phone"
        ]
