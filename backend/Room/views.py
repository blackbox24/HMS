from django.shortcuts import render
from rest_framework import generics
from .models import Room
from .serializers import  RoomSerializer

# Create 
class CreateRoom(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

# Fetch By ID
class FetchSingleRoom(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = 'pk'

# Update 
class UpdateRoom(generics.RetrieveUpdateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = 'pk'

# delete
class DeleteRoom(generics.DestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    
    def perform_destroy(self, instance):
        return super().perform_destroy(instance)

# ReadAll
class FetchAllRoom(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

