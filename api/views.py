from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Register, AppUser
from .serializers import *
from accounts.models import Users
from django.utils.timezone import now
from rest_framework_simplejwt.views import TokenObtainPairView




class AppUserTokenObtainPairView(TokenObtainPairView):
    serializer_class = AppUserTokenObtainPairSerializer

    

@api_view(['POST'])
def register_app_user(request):
    """
    Register a new app user using a serializer for validation.
    """
    serializer = AppUserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        name = serializer.validated_data['name']

        try:
            # Create main user and app user
            user = Users.objects.create_user(email=email, password=password, first_name=name)
            app_user = AppUser.objects.create(user=user)

            return Response({
                "message": "App user registered successfully",
                "api_key": app_user.api_key,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_registration_details(request):
    """
    Use a serializer to return registration details.
    """
    registration_number = request.query_params.get('registration_number')
    try:
        registration = Register.objects.get(registration_number=registration_number)
        serializer = RegisterSerializer(registration)
        return Response(serializer.data, status=200)
    except Register.DoesNotExist:
        return Response({"error": "Registration not found"}, status=404)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_registration(request):
    """
    Validate a registration using serializers for input validation and response.
    """
    registration_number = request.data.get('registration_number')
    try:
        registration = Register.objects.get(registration_number=registration_number)

        if registration.validated:
            return Response({"message": "Already validated"}, status=200)

        registration.validated = True
        registration.validated_at = now()
        registration.validated_by = request.user.email
        registration.save()

        serializer = RegisterSerializer(registration)
        return Response({"message": "Registration validated successfully", "data": serializer.data}, status=200)
    except Register.DoesNotExist:
        return Response({"error": "Registration not found"}, status=404)
