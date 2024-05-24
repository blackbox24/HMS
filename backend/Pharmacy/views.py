from django.shortcuts import render
from rest_framework import generics
from .models import Pharmacy
from .serializers import  PharmacySerializer

# Create 
class CreatePharmacy(generics.CreateAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer

# Fetch By ID
class FetchSinglePharmacy(generics.RetrieveAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    lookup_field = 'pk'

# Update 
class UpdatePharmacy(generics.RetrieveUpdateAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    lookup_field = 'pk'

# delete
class DeletePharmacy(generics.DestroyAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllPharmacy(generics.ListAPIView):
    queryset = Pharmacy.objects.all()
    serializer_class = PharmacySerializer

