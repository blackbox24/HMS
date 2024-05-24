
from django.shortcuts import render
from rest_framework import generics
from .models import Doctor
from .serializers import  DoctorSerializer

# Create 
class CreateDoctor(generics.CreateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

# Fetch By ID
class FetchSingleDoctor(generics.RetrieveAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'pk'

# Update 
class UpdateDoctor(generics.RetrieveUpdateAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = 'pk'

# delete
class DeleteDoctor(generics.DestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllDoctor(generics.ListAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

