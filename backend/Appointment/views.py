from django.shortcuts import render
from rest_framework import generics
from models import Appointment
from serializers import  AppointmentSerializer

# Create 
class CreateAppointment(generics.CreateAPIView):
    queryset = Appointment
    serializer_class = AppointmentSerializer

# Fetch By ID
class FetchSingleAppointment(generics.RetrieveAPIView):
    queryset = Appointment
    serializer_class = AppointmentSerializer
    lookup_field = 'pk'

# Update 
class UpdateAppointment(generics.RetrieveUpdateAPIView):
    queryset = Appointment
    serializer_class = AppointmentSerializer
    lookup_field = 'pk'

# delete
class DeleteAppointment(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Appointment
    serializer_class = AppointmentSerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllAppointment(generics.RetrieveAPIView):
    queryset = Appointment
    serializer_class = AppointmentSerializer

