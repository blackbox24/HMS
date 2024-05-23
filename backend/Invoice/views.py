from django.shortcuts import render
from rest_framework import generics
from models import Invoice
from serializers import  InvoiceSerializer

# Create 
class CreateInvoice(generics.CreateAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer

# Fetch By ID
class FetchSingleInvoice(generics.RetrieveAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer
    lookup_field = 'pk'

# Update 
class UpdateInvoice(generics.RetrieveUpdateAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer
    lookup_field = 'pk'

# delete
class DeleteInvoice(generics.RetrieveDestroyAPIViewAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer
    lookup_field = 'pk'

# ReadAll
class FetchAllInvoice(generics.RetrieveAPIView):
    queryset = Invoice
    serializer_class = InvoiceSerializer

