from django.shortcuts import render
from rest_framework import generics
from .models import Patient
from .serializers import  PatientSerializer

# Create 
class CreatePatient(generics.CreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

# Fetch By ID
class FetchSinglePatient(generics.RetrieveAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'pk'

# Update 
class UpdatePatient(generics.RetrieveUpdateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    lookup_field = 'pk'

# delete
class DeletePatient(generics.DestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllPatient(generics.ListAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

