from django.shortcuts import render
from rest_framework import generics
from models import Prescription
from serializers import  PrescriptionSerializer

# Create 
class CreatePrescription(generics.CreateAPIView):
    queryset = Prescription
    serializer_class = PrescriptionSerializer

# Fetch By ID
class FetchSinglePrescription(generics.RetrieveAPIView):
    queryset = Prescription
    serializer_class = PrescriptionSerializer
    lookup_field = 'pk'

# Update 
class UpdatePrescription(generics.RetrieveUpdateAPIView):
    queryset = Prescription
    serializer_class = PrescriptionSerializer
    lookup_field = 'pk'

# delete
class DeletePrescription(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Prescription
    serializer_class = PrescriptionSerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllPrescription(generics.RetrieveAPIView):
    queryset = Prescription
    serializer_class = PrescriptionSerializer

