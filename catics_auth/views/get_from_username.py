from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication

User = get_user_model()

class GetFromUsernameSerializer(serializers.Serializer):
    username = serializers.CharField()

class GetFromUsernameView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = GetFromUsernameSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.validated_data

        users = User.objects.filter(username=data['username'])
        if not users.exists():
            return Response(status=404)
        return Response({ 'id': users.first().id })

