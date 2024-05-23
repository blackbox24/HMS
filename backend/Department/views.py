from django.shortcuts import render
from rest_framework import generics
from models import Department
from serializers import  DepartmentSerializer

# Create Hospitals
class CreateDepartment(generics.CreateAPIView):
    queryset = Department
    serializer_class = DepartmentSerializer

# Fetch By ID
class FetchSingleDepartment(generics.RetrieveAPIView):
    queryset = Department
    serializer_class = DepartmentSerializer
    lookup_field = 'pk'

# Update 
class UpdateDepartment(generics.RetrieveUpdateAPIView):
    queryset = Department
    serializer_class = DepartmentSerializer
    lookup_field = 'pk'

# delete
class DeleteDepartment(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Department
    serializer_class = DepartmentSerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllDepartment(generics.RetrieveAPIView):
    queryset = Department
    serializer_class = DepartmentSerializer

