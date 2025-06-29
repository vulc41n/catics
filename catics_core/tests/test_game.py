from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from catics_auth.models import Validation
from ..models import Agent, Game
from ..game_state import Board, Position
from .helpers import all_units, PASSWORD

User = get_user_model()

class GameTestCase(APITestCase):
    def setUp(self):
        self.player1 = User.objects.create_user(
            username='player1',
            email='player1@catics.fr',
            password=PASSWORD,
        )
        Validation.objects.create(
            user=self.player1,
            expire_at=timezone.now(),
            validation_code='',
            is_validated=True,
        )
        response = self.client.post(
            reverse('auth-login'),
            { 'username': 'player1', 'password': PASSWORD },
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + response.data['token'])

        self.player2 = User.objects.create_user(
            username='player2',
            email='player2@catics.fr',
            password=PASSWORD,
        )
        Validation.objects.create(
            user=self.player2,
            expire_at=timezone.now(),
            validation_code='',
            is_validated=True,
        )

    def test_unvalidated(self):
        Validation.objects.filter(user=self.player1).update(is_validated=False)
        response = self.client.put(
            reverse('core-game'),
            { 'player2_user': self.player2.id },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'].code, 'unvalidated')
        self.assertFalse(Game.objects.filter(player2_id=self.player2.id).exists())

    def test_unlogged(self):
        self.client.credentials()
        response = self.client.put(
            reverse('core-game'),
            { 'player2_user': self.player2.id },
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')
        self.assertFalse(Game.objects.filter(player2_id=self.player2.id).exists())

    def test_spectator(self):
        response = self.client.put(
            reverse('core-game'),
            { 'player2_user': self.player2.id },
        )
        id = response.data['id']

        spectator = User.objects.create_user(
            username='spectator',
            email='spectator@catics.fr',
            password=PASSWORD,
        )
        Validation.objects.create(
            user=spectator,
            expire_at=timezone.now(),
            validation_code='',
            is_validated=True,
        )
        response = self.client.post(
            reverse('auth-login'),
            { 'username': 'spectator', 'password': PASSWORD },
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + response.data['token'])

        response = self.client.get(
            reverse('core-game'),
            { 'id': id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('board', response.data)
        self.assertEqual(len(response.data['board']), 0)

    def test_p2_not_found(self):
        Agent.objects.create(
            id=self.player2.id + 1,
            owner=self.player1,
            name='agent id exists while user doesn\'t',
        )
        response = self.client.put(
            reverse('core-game'),
            { 'player2_user': self.player2.id + 1 },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['player2_user'][0].code, 'does_not_exist')

    def test_get_not_found(self):
        response = self.client.get(
            reverse('core-game'),
            { 'id': 0 },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['id'][0].code, 'does_not_exist')

    def test_pvp(self):
        response = self.client.put(
            reverse('core-game'),
            { 'player2_user': self.player2.id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        id = response.data['id']
        response = self.client.get(
            reverse('core-game'),
            { 'id': id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('board', response.data)
        self.assertEqual(len(response.data['board']), 0)

    def test_get_basic(self):
        response = self.client.put(
            reverse('core-game'),
            { 'player2_user': self.player2.id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        id = response.data['id']
        game = Game.objects.get(id=id)
        all_units(game, False, skip_last_move=True)
        response = self.client.get(
            reverse('core-game'),
            { 'id': id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('board', response.data)
        self.assertIn('player1_user', response.data)
        self.assertIn('player2_user', response.data)
        self.assertIn('is_p1_turn', response.data)
        self.assertIn('n_kittens_p1', response.data)
        self.assertIn('n_cats_p1', response.data)
        self.assertIn('n_kittens_p2', response.data)
        self.assertIn('n_cats_p2', response.data)
        self.assertNotIn('winner', response.data)
        board = Board(response.data['board'])
        self.assertEqual(len(board), 8)
        self.assertEqual(board.get(0, 0), Position(False, False))
        self.assertEqual(board.get(2, 1), Position(True, False))
        self.assertEqual(board.get(4, 1), Position(True, False))
        self.assertEqual(board.get(0, 2), Position(True, False))
        self.assertEqual(board.get(4, 2), Position(True, False))
        self.assertEqual(board.get(0, 3), Position(True, False))
        self.assertEqual(board.get(2, 4), Position(True, False))
        self.assertEqual(board.get(4, 4), Position(True, False))
        self.assertEqual(response.data['player1_user'], self.player1.username)
        self.assertEqual(response.data['player2_user'], self.player2.username)
        self.assertEqual(response.data['is_p1_turn'], True)
        self.assertEqual(response.data['n_kittens_p1'], 1)
        self.assertEqual(response.data['n_cats_p1'], 0)
        self.assertEqual(response.data['n_kittens_p2'], 7)
        self.assertEqual(response.data['n_cats_p2'], 0)

    def test_get_promote(self):
        response = self.client.put(
            reverse('core-game'),
            { 'player2_user': self.player2.id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        id = response.data['id']
        game = Game.objects.get(id=id)
        all_units(game, False, with_line=True)
        response = self.client.get(
            reverse('core-game'),
            { 'id': id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('board', response.data)
        self.assertIn('player1_user', response.data)
        self.assertIn('player2_user', response.data)
        self.assertIn('is_p1_turn', response.data)
        self.assertIn('n_kittens_p1', response.data)
        self.assertIn('n_cats_p1', response.data)
        self.assertIn('n_kittens_p2', response.data)
        self.assertIn('n_cats_p2', response.data)
        self.assertIn('promotions', response.data)
        self.assertNotIn('winner', response.data)
        board = Board(response.data['board'])
        self.assertEqual(len(board), 9)
        self.assertEqual(board.get(2, 1), Position(True, False))
        self.assertEqual(board.get(4, 1), Position(True, False))
        self.assertEqual(board.get(0, 2), Position(True, False))
        self.assertEqual(board.get(4, 2), Position(True, False))
        self.assertEqual(board.get(0, 3), Position(True, False))
        self.assertEqual(board.get(4, 3), Position(True, False))
        self.assertEqual(board.get(2, 4), Position(True, False))
        self.assertEqual(board.get(0, 5), Position(True, False))
        self.assertEqual(board.get(4, 5), Position(False, False))
        self.assertEqual(response.data['player1_user'], self.player1.username)
        self.assertEqual(response.data['player2_user'], self.player2.username)
        self.assertEqual(response.data['is_p1_turn'], True)
        self.assertEqual(response.data['n_kittens_p1'], 0)
        self.assertEqual(response.data['n_cats_p1'], 0)
        self.assertEqual(response.data['n_kittens_p2'], 7)
        self.assertEqual(response.data['n_cats_p2'], 0)
        self.assertEqual(len(response.data['promotions']), 9)
        self.assertIn([[2, 1]], response.data['promotions'])
        self.assertIn([[4, 1]], response.data['promotions'])
        self.assertIn([[0, 2]], response.data['promotions'])
        self.assertIn([[4, 2]], response.data['promotions'])
        self.assertIn([[0, 3]], response.data['promotions'])
        self.assertIn([[4, 3]], response.data['promotions'])
        self.assertIn([[2, 4]], response.data['promotions'])
        self.assertIn([[0, 5]], response.data['promotions'])
        is_line_in_promotions = False
        for p in response.data['promotions']:
            if len(p) == 3:
                is_line_in_promotions = True
                self.assertIn([4, 1], p)
                self.assertIn([4, 2], p)
                self.assertIn([4, 3], p)
                break
        self.assertTrue(is_line_in_promotions)

    def test_get_win(self):
        response = self.client.put(
            reverse('core-game'),
            { 'player2_user': self.player2.id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('id', response.data)
        id = response.data['id']
        game = Game.objects.get(id=id)
        # cats only
        game.n_cats_p1 += 8
        game.n_kittens_p1 -= 8
        game.n_cats_p2 += 8
        game.n_kittens_p2 -= 8
        all_units(game, True)
        response = self.client.get(
            reverse('core-game'),
            { 'id': id },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('board', response.data)
        self.assertIn('player1_user', response.data)
        self.assertIn('player2_user', response.data)
        self.assertNotIn('is_p1_turn', response.data)
        self.assertIn('n_kittens_p1', response.data)
        self.assertIn('n_cats_p1', response.data)
        self.assertIn('n_kittens_p2', response.data)
        self.assertIn('n_cats_p2', response.data)
        self.assertIn('winner', response.data)
        board = Board(response.data['board'])
        self.assertEqual(len(board), 9)
        self.assertEqual(board.get(0, 0), Position(False, True))
        self.assertEqual(board.get(2, 1), Position(True, True))
        self.assertEqual(board.get(4, 1), Position(True, True))
        self.assertEqual(board.get(0, 2), Position(True, True))
        self.assertEqual(board.get(4, 2), Position(True, True))
        self.assertEqual(board.get(0, 3), Position(True, True))
        self.assertEqual(board.get(2, 4), Position(True, True))
        self.assertEqual(board.get(4, 4), Position(True, True))
        self.assertEqual(board.get(0, 5), Position(True, True))
        self.assertEqual(response.data['player1_user'], self.player1.username)
        self.assertEqual(response.data['player2_user'], self.player2.username)
        self.assertEqual(response.data['winner'], '1')
        self.assertEqual(response.data['n_kittens_p1'], 0)
        self.assertEqual(response.data['n_cats_p1'], 0)
        self.assertEqual(response.data['n_kittens_p2'], 0)
        self.assertEqual(response.data['n_cats_p2'], 7)
