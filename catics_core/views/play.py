from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from catics_auth.permissions import IsValidated
from ..models import Game
from ..game_state import GameState
from .exceptions import NotYourTurnException, NotAPlayerException

class PlaySerializer(serializers.Serializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    x = serializers.IntegerField(min_value=0, max_value=5)
    y = serializers.IntegerField(min_value=0, max_value=5)
    is_cat = serializers.BooleanField()

class PlayView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsValidated]

    def post(self, request, format=None):
        serializer = PlaySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.validated_data

        is_player1 = request.user.id == data['game'].player1_id
        is_player2 = request.user.id == data['game'].player2_id

        if not is_player1 and not is_player2:
            raise NotAPlayerException()
            
        if is_player1 != data['game'].is_p1_turn:
            raise NotYourTurnException()

        state = GameState(data['game'])
        state.play(data['x'], data['y'], data['is_cat'])
        state.save()
        data['game'].refresh_from_db()
        return Response({ 'board': data['game'].board })

