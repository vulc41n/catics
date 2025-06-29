from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from knox.auth import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ..models import Validation

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def am_i_logged(request):
    return Response(True)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def is_validated(request):
    validations = Validation.objects.filter(Q(is_validated=True) & Q(user=request.user))
    return Response(validations.exists())

