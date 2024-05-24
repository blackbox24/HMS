from rest_framework import serializers
from Auth.models import UserData
from Staff.models import Staff


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserData
        fields = ['id', 'first_name', 'last_name', 'email', 'staff_id']

class RegistrationSerializer(serializers.ModelSerializer):
    staff_id = serializers.PrimaryKeyRelatedField(queryset=Staff.objects.all())

    class Meta:
        model = UserData
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'password', 
            'staff_id'
        ]


    def create(self, validated_data):
        staff_id = validated_data.pop('staff_id')
        user = UserData.objects.create_user(staff_id=staff_id, **validated_data)
        user.save()
        return user
    
    
class PasswordResetSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password")
        return value

    def validate_new_password(self, value):
        # Add any custom validation for new password here
        return value