from django.shortcuts import render
from rest_framework import generics
from models import Patient
from serializers import  PatientSerializer

# Create 
class CreatePatient(generics.CreateAPIView):
    queryset = Patient
    serializer_class = PatientSerializer

# Fetch By ID
class FetchSinglePatient(generics.RetrieveAPIView):
    queryset = Patient
    serializer_class = PatientSerializer
    lookup_field = 'pk'

# Update 
class UpdatePatient(generics.RetrieveUpdateAPIView):
    queryset = Patient
    serializer_class = PatientSerializer
    lookup_field = 'pk'

# delete
class DeletePatient(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Patient
    serializer_class = PatientSerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllPatient(generics.RetrieveAPIView):
    queryset = Patient
    serializer_class = PatientSerializer

