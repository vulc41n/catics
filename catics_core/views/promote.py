from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from catics_auth.permissions import IsValidated
from ..game_state import GameState
from ..models import Game
from .exceptions import NotYourTurnException, InvalidUnitsException, NotAPlayerException

class PromoteSerializer(serializers.Serializer):
    game = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())
    units = serializers.ListField(
        child=serializers.ListField(
            child=serializers.IntegerField(min_value=0, max_value=6),
            min_length=2,
            max_length=2,
        ),
    )

class PromoteView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsValidated]

    def post(self, request, format=None):
        serializer = PromoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.validated_data

        if data['game'].is_p1_turn:
            (current_model, opponent_model, current_player, opponent_player) = (
                data['game'].player1_type.model,
                data['game'].player2_type.model,
                data['game'].player1_id,
                data['game'].player2_id,
            )
        else:
            (current_model, opponent_model, current_player, opponent_player) = (
                data['game'].player2_type.model,
                data['game'].player1_type.model,
                data['game'].player2_id,
                data['game'].player1_id,
            )

        # is the user the opponent ?
        if opponent_model == 'caticsuser' and opponent_player == request.user.id:
            raise NotYourTurnException()

        # is the user the current player ?
        if current_model != 'caticsuser' or current_player != request.user.id:
            raise NotAPlayerException()

        promotion_index = None
        for (i, p) in enumerate(data['game'].promotions):
            if p == data['units']:
                promotion_index = i
                break
        if promotion_index is None:
            raise InvalidUnitsException()

        state = GameState(data['game'])
        state.promote(promotion_index)
        state.is_p1_turn = not state.is_p1_turn
        state.save()

        return Response({ 'board': state.board.value() })

