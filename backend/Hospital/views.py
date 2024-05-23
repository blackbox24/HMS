from django.shortcuts import render
from rest_framework import generics
from models import Hospital
from serializers import HospitalSerializer

# Create Hospitals
class CreateHospital(generics.CreateAPIView):
    queryset = Hospital
    serializer_class = HospitalSerializer

# Fetch By ID
class FetchSingleHospital(generics.RetrieveAPIView):
    queryset = Hospital
    serializer_class = HospitalSerializer
    lookup_field = 'h_id'

# Update 
class UpdateHospital(generics.RetrieveUpdateAPIView):
    queryset = Hospital
    serializer_class = HospitalSerializer
    lookup_field = 'h_id'

# delete
class DeleteHospital(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Hospital
    serializer_class = HospitalSerializer
    lookup_field = 'h_id'

# ReadAll
class FetchAllHospital(generics.RetrieveAPIView):
    queryset = Hospital
    serializer_class = HospitalSerializer

