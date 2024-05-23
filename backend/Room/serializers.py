from rest_framework import serializers
from models import Room
from staff.models import Staff
from Patient.models import Patient

class RoomSerializer(serializers.ModelSerializer):
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    staff_id = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())

    class Meta:
        model = Room
        fields = [
            "room_num",
            "patient_id",
            "staff_id",
            "admission_date",
            "max_quantity"
        ] 
