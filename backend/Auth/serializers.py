from rest_framework import serializers
from Auth.models import UserData
from staff.models import Staff

class RegistrationSerializer(serializers.ModelSerializer):
    staff_id = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())

    class Meta:
        model = UserData
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'password', 
            'staff_id'
        ]


    def create(self, validated_data):
        staff_id = validated_data.pop('staff_id')
        user = UserData.objects.create_user(staff_id=staff_id, **validated_data)
        return user
