from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name="sign_up"),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/', TokenAPIView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('verified/', verified, name='verified'),
    path('invalid-token/', invalid_token, name='invalid_token'),
]