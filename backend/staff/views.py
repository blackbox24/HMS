from django.shortcuts import render
from rest_framework import generics
from models import Staff
from serializers import  StaffSerializer

# Create 
class CreateStaff(generics.CreateAPIView):
    queryset = Staff
    serializer_class = StaffSerializer

# Fetch By ID
class FetchSingleStaff(generics.RetrieveAPIView):
    queryset = Staff
    serializer_class = StaffSerializer
    lookup_field = 'pk'

# Update 
class UpdateStaff(generics.RetrieveUpdateAPIView):
    queryset = Staff
    serializer_class = StaffSerializer
    lookup_field = 'pk'

# delete
class DeleteStaff(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Staff
    serializer_class = StaffSerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllStaff(generics.RetrieveAPIView):
    queryset = Staff
    serializer_class = StaffSerializer

