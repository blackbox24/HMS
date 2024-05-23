from django.shortcuts import render
from rest_framework import generics
from models import Room
from serializers import  RoomSerializer

# Create 
class CreateRoom(generics.CreateAPIView):
    queryset = Room
    serializer_class = RoomSerializer

# Fetch By ID
class FetchSingleRoom(generics.RetrieveAPIView):
    queryset = Room
    serializer_class = RoomSerializer
    lookup_field = 'pk'

# Update 
class UpdateRoom(generics.RetrieveUpdateAPIView):
    queryset = Room
    serializer_class = RoomSerializer
    lookup_field = 'pk'

# delete
class DeleteRoom(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Room
    serializer_class = RoomSerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllRoom(generics.RetrieveAPIView):
    queryset = Room
    serializer_class = RoomSerializer

