from rest_framework import serializers
from models import Department
from Hospital.models import Hospital

class DepartmentSerializer(serializers.ModelSerializer):
    hospital_id = serializers.PrimaryKeyRelatedField(queryset=Hospital.object.all())
    class Meta:
        model = Department
        fields = [
            'department_name',
            'hospital_id'
        ]

    