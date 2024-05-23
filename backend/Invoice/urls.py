from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllInvoice.as_view(), name="all_invoice"),
    path('add/', CreateInvoice.as_view(), name="add_invoice"),
    path('update/<int:pk>/', UpdateInvoice.as_view(), name="update_invoice"),
    path('edit/<int:pk>/', FetchSingleInvoice.as_view(), name="edit_invoice"),
    path('remove/<int:pk>/', DeleteInvoice.as_view(), name="remove_invoice"),
]