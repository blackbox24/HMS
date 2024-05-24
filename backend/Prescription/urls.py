from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllPrescription.as_view(), name="all_Prescription"),
    path('add/', CreatePrescription.as_view(), name="add_Prescription"),
    path('update/<int:pk>/', UpdatePrescription.as_view(), name="update_Prescription"),
    path('edit/<int:pk>/', FetchSinglePrescription.as_view(), name="edit_Prescription"),
    path('remove/<int:pk>/', DeletePrescription.as_view(), name="remove_Prescription"),
]