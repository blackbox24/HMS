from rest_framework import serializers
from models import * 
from Department.models import Department

class staffSerializer(serializers.ModelSerializer):
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
