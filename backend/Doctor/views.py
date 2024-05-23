from django.shortcuts import render
from rest_framework import generics
from models import Doctor
from serializers import  DoctorSerializer

# Create 
class CreateDoctor(generics.CreateAPIView):
    queryset = Doctor
    serializer_class = DoctorSerializer

# Fetch By ID
class FetchSingleDoctor(generics.RetrieveAPIView):
    queryset = Doctor
    serializer_class = DoctorSerializer
    lookup_field = 'pk'

# Update 
class UpdateDoctor(generics.RetrieveUpdateAPIView):
    queryset = Doctor
    serializer_class = DoctorSerializer
    lookup_field = 'pk'

# delete
class DeleteDoctor(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Doctor
    serializer_class = DoctorSerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllDoctor(generics.RetrieveAPIView):
    queryset = Doctor
    serializer_class = DoctorSerializer

