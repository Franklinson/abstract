from django.urls import path
from .views import register_app_user, get_registration_details, validate_registration

urlpatterns = [
    path('app_user/register/', register_app_user, name='register_app_user'),
    path('validate_registration/', get_registration_details, name='get_registration_details'),
    path('alidate_registration/validate/', validate_registration, name='validate_registration'),
]
