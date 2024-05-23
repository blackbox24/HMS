from rest_framework import generics
from rest_framework.response import Response
from .serializers import RegistrationSerializer
from .models import UserData
from staff.models import Staff

class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name = serializer.validated_data['first_name']
        last_name = serializer.validated_data['last_name']
        username = f"{first_name[0].lower()}{last_name.lower()}"
        
        
        user = UserData.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=serializer.validated_data['email'],
            phone_number=serializer.validated_data['phone_number'],
            password=serializer.validated_data['password'],
            staff_id=serializer.validated_data['staff_id']
        )
        return Response(serializer)