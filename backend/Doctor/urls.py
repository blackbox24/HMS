from django.urls import path
from .views import *

urlpatterns = [
    path('', FetchAllDoctor.as_view(), name="all_doctor"),
    path('add/', CreateDoctor.as_view(), name="add_doctor"),
    path('update/<int:pk>/', UpdateDoctor.as_view(), name="update_doctor"),
    path('edit/<int:pk>/', FetchSingleDoctor.as_view(), name="edit_doctor"),
    path('remove/<int:pk>/', DeleteDoctor.as_view(), name="remove_doctor"),
]