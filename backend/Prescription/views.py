from django.shortcuts import render
from rest_framework import generics
from .models import Prescription
from .serializers import  PrescriptionSerializer

# Create 
class CreatePrescription(generics.CreateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

# Fetch By ID
class FetchSinglePrescription(generics.RetrieveAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    lookup_field = 'pk'

# Update 
class UpdatePrescription(generics.RetrieveUpdateAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    lookup_field = 'pk'

# delete
class DeletePrescription(generics.DestroyAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllPrescription(generics.ListAPIView):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

