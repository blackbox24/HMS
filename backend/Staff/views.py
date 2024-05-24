from django.shortcuts import render
from rest_framework import generics
from .models import Staff
from .serializers import  StaffSerializer

# Create 
class CreateStaff(generics.CreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

# Fetch By ID
class FetchSingleStaff(generics.RetrieveAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    lookup_field = 'pk'

# Update 
class UpdateStaff(generics.RetrieveUpdateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    lookup_field = 'pk'

# delete
class DeleteStaff(generics.DestroyAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllStaff(generics.ListAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer

