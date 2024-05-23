from django.shortcuts import render
from rest_framework import generics
from models import Pharmacy
from serializers import  PharmacySerializer

# Create 
class CreatePharmacy(generics.CreateAPIView):
    queryset = Pharmacy
    serializer_class = PharmacySerializer

# Fetch By ID
class FetchSinglePharmacy(generics.RetrieveAPIView):
    queryset = Pharmacy
    serializer_class = PharmacySerializer
    lookup_field = 'pk'

# Update 
class UpdatePharmacy(generics.RetrieveUpdateAPIView):
    queryset = Pharmacy
    serializer_class = PharmacySerializer
    lookup_field = 'pk'

# delete
class DeletePharmacy(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Pharmacy
    serializer_class = PharmacySerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllPharmacy(generics.RetrieveAPIView):
    queryset = Pharmacy
    serializer_class = PharmacySerializer

