from django.shortcuts import render
from rest_framework import generics
from .models import Appointment
from .serializers import  AppointmentSerializer

# Create 
class CreateAppointment(generics.CreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

# Fetch By ID
class FetchSingleAppointment(generics.RetrieveAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    lookup_field = 'pk'

# Update 
class UpdateAppointment(generics.RetrieveUpdateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    lookup_field = 'pk'

# delete
class DeleteAppointment(generics.DestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllAppointment(generics.ListAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

