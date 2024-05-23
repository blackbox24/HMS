from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllPharmacy.as_view(), name="all_pharmacy"),
    path('add/', CreatePharmacy.as_view(), name="add_pharmacy"),
    path('update/<int:pk>/', UpdatePharmacy.as_view(), name="update_pharmacy"),
    path('edit/<int:pk>/', FetchSinglePharmacy.as_view(), name="edit_pharmacy"),
    path('remove/<int:pk>/', DeletePharmacy.as_view(), name="remove_pharmacy"),
]