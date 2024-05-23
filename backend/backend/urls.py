from django.contrib import admin
from django.urls import path,include

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="API Docs",
      default_version='v1',
      description="Todo Application ",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@xyz.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


    
    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/',include('Auth.urls')),
    path('api/staff/',include('staff.urls')),
    path('api/hosptial/',include('Hospital.urls')),
    path('api/department/',include('Department.urls')),
    path('api/doctor/',include('Doctor.urls')),
    path('api/pharmacy/',include('Pharmacy.urls')),
    path('api/patient/',include('Patient.urls')),
    path('api/prescription/',include('Prescription.urls')),
    path('api/room/',include('Room.urls')),
    path('api/invoice/',include('Invoice.urls')),
    path('api/appointment/',include('Appointment.urls')),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]



