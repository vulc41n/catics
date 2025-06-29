from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from knox.auth import TokenAuthentication
from catics_auth.permissions import IsValidated
from ..models import Game, Agent

User = get_user_model()

class GameCreateSerializer(serializers.Serializer):
    player1_agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all(), required=False)
    player2_agent = serializers.PrimaryKeyRelatedField(queryset=Agent.objects.all(), required=False)
    player2_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    def validate(self, data):
        if 'player2_agent' not in data and 'player2_user' not in data:
            raise ValidationError(
                'Veuillez renseigner un des deux champs "player2_agent" ou "player2_user"'
            )
        if 'player2_agent' in data and 'player2_user' in data:
            raise ValidationError(
                'Veuillez supprimer un des deux champs "player2_agent" ou "player2_user"'
            )
        return data

class GameGetSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Game.objects.all())

class GameView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsValidated]

    def get(self, request, format=None):
        serializer = GameGetSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        game = serializer.validated_data['id']
        result = {
            'board': game.board,
            'n_kittens_p1': game.n_kittens_p1,
            'n_cats_p1': game.n_cats_p1,
            'n_kittens_p2': game.n_kittens_p2,
            'n_cats_p2': game.n_cats_p2,
        }
        if len(game.promotions) > 0:
            result['promotions'] = game.promotions
        if game.winner == 'n':
            result['is_p1_turn'] = game.is_p1_turn
        else:
            result['winner'] = game.winner
        if game.player1_type.model == 'caticsuser':
            result['player1_user'] = game.player1_object.username
        else:
            # TODO: agents
            pass
        if game.player2_type.model == 'caticsuser':
            result['player2_user'] = game.player2_object.username
        else:
            # TODO: agents
            pass
        return Response(result)

    def put(self, request, format=None):
        serializer = GameCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        data = serializer.validated_data

        if 'player1_agent' in data:
            # TODO
            pass
        else:
            player1_object = request.user
        if 'player2_agent' in data:
            # TODO
            pass
        else:
            player2_object = data['player2_user']
        game = Game.objects.create(player1_object=player1_object, player2_object=player2_object)
        return Response({ 'id': game.id })
