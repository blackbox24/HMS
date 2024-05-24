from django.shortcuts import render
from rest_framework import generics
from .models import Department
from .serializers import  DepartmentSerializer

# Create Hospitals
class CreateDepartment(generics.CreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

# Fetch By ID
class FetchSingleDepartment(generics.RetrieveAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = 'pk'

# Update 
class UpdateDepartment(generics.RetrieveUpdateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    lookup_field = 'pk'

# delete
class DeleteDepartment(generics.DestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllDepartment(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

