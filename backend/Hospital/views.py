from django.shortcuts import render
from rest_framework import generics
from .models import Hospital
from .serializers import HospitalSerializer

# Create Hospitals
class CreateHospital(generics.CreateAPIView):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

# Fetch By ID
class FetchSingleHospital(generics.RetrieveAPIView):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    lookup_field = 'pk'

# Update 
class UpdateHospital(generics.RetrieveUpdateAPIView):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    lookup_field = 'pk'

# delete
class DeleteHospital(generics.DestroyAPIView):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllHospital(generics.ListAPIView):
    queryset = Hospital.objects.all()
    serializer_class = HospitalSerializer

