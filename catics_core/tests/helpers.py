from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from catics_auth.models import Validation
from ..game_state import GameState
from ..models import Game

User = get_user_model()

PASSWORD = 'test123!.@'

def two_players_setup(case):
    case.player1 = User.objects.create_user(
        username='player1',
        email='player1@catics.fr',
        password=PASSWORD,
    )
    Validation.objects.create(
        user=case.player1,
        expire_at=timezone.now(),
        validation_code='',
        is_validated=True,
    )
    response = case.client.post(
        reverse('auth-login'),
        { 'username': 'player1', 'password': PASSWORD },
    )
    case.token1 = response.data['token']
    case.client.credentials(HTTP_AUTHORIZATION="Token " + case.token1)

    case.player2 = User.objects.create_user(
        username='player2',
        email='player2@catics.fr',
        password=PASSWORD,
    )
    Validation.objects.create(
        user=case.player2,
        expire_at=timezone.now(),
        validation_code='',
        is_validated=True,
    )
    response = case.client.post(
        reverse('auth-login'),
        { 'username': 'player2', 'password': PASSWORD },
    )
    case.token2 = response.data['token']
    case.game = Game.objects.create(
        player1_object=case.player1,
        player2_object=case.player2,
    )

'''
without line :
+-----+-----+-----+-----+-----+-----+
| p2x |     |     |     |     |     |
+-----+-----+-----+-----+-----+-----+
|     |     | p1x |     | p1x |     |
+-----+-----+-----+-----+-----+-----+
| p1x |     |     |     | p1x |     |
+-----+-----+-----+-----+-----+-----+
| p1x |     |     |     |     |     |
+-----+-----+-----+-----+-----+-----+
|     |     | p1x |     | p1x |     |
+-----+-----+-----+-----+-----+-----+
|?p1x?|     |     |     |     |     |
+-----+-----+-----+-----+-----+-----+

with line :
+-----+-----+-----+-----+-----+-----+
|     |     |     |     |     |     |
+-----+-----+-----+-----+-----+-----+
|     |     | p1x |     | p1x |     |
+-----+-----+-----+-----+-----+-----+
| p1x |     |     |     | p1x |     |
+-----+-----+-----+-----+-----+-----+
| p1x |     |     |     | p1x |     |
+-----+-----+-----+-----+-----+-----+
|     |     | p1x |     |     |     |
+-----+-----+-----+-----+-----+-----+
|?p1x?|     |     |     | p2x |     |
+-----+-----+-----+-----+-----+-----+
'''
def all_units(game: Game, are_cats: bool, skip_last_move: bool = False, with_line: bool = False):
    state = GameState(game)
    state.play(2, 2, are_cats)
    state.play(5, 5, are_cats)
    state.play(4, 4, are_cats)
    state.play(0, 5, are_cats)
    state.play(1, 4, are_cats)
    state.play(5, 0, are_cats)
    state.play(4, 1, are_cats)
    state.play(0, 0, are_cats)
    state.play(1, 1, are_cats)
    state.play(2, 0, are_cats)
    state.play(2, 1, are_cats)
    state.play(2, 5, are_cats)
    state.play(2, 4, are_cats)
    if with_line:
        state.play(4, 5, are_cats)
    else:
        state.play(0, 0, are_cats)
    if not skip_last_move:
        state.play(0, 5, are_cats)
    state.save()
