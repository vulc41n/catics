from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from catics_auth.models import Validation
from ..game_state import GameState, Board, Position
from .helpers import two_players_setup, all_units, PASSWORD

User = get_user_model()

class PromoteTestCase(APITestCase):
    def setUp(self):
        two_players_setup(self)

    '''
    +-----+-----+-----+-----+-----+-----+
    | p1k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     | p2k |     |
    +-----+-----+-----+-----+-----+-----+
    | p1k | p1k | p1k | p1k |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     | p2k |
    +-----+-----+-----+-----+-----+-----+
    | p2k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def double_lines_setup(self):
        state = GameState(self.game)
        state.play(0, 0, False)
        state.play(0, 5, False)
        state.play(2, 2, False)
        state.play(5, 5, False)
        state.play(3, 2, False)
        state.play(4, 2, False)
        state.play(4, 3, False)
        state.play(5, 4, False)
        state.play(0, 2, False)
        state.save()

    def test_unlogged(self):
        self.double_lines_setup()

        self.client.credentials()
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [0, 2], [1, 2], [2, 2] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')
        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 8)

    def test_unvalidated(self):
        Validation.objects.filter(user=self.player1).update(is_validated=False)

        self.double_lines_setup()
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [0, 2], [1, 2], [2, 2] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'].code, 'unvalidated')

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 8)

    def test_invalid_units(self):
        self.double_lines_setup()
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [0, 0], [1, 2], [2, 2] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'invalid_units')

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 8)

    def test_wrong_player(self):
        self.double_lines_setup()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [0, 0], [1, 2], [2, 2] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'not_your_turn')

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 8)

    def test_third_user(self):
        other = User.objects.create_user(
            username='other',
            email='other@catics.fr',
            password=PASSWORD,
        )
        Validation.objects.create(
            user=other,
            expire_at=timezone.now(),
            validation_code='',
        )
        Validation.objects.filter(user=other).update(is_validated=True)
        response = self.client.post(
            reverse('auth-login'),
            { 'username': 'other', 'password': PASSWORD },
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + response.data['token'])
        self.double_lines_setup()

        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [0, 0], [1, 2], [2, 2] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'].code, 'not_a_player')

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 8)

    def test_double_lines(self):
        self.double_lines_setup()
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [0, 2], [1, 2], [2, 2] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)

        # can player 2 play after promotion ?
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 5, 'y': 0 },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 6)
        self.assertEqual(board.get(0, 0), Position(True, False))
        self.assertEqual(board.get(0, 5), Position(False, False))
        self.assertEqual(board.get(3, 2), Position(True, False))
        self.assertEqual(board.get(4, 1), Position(False, False))
        self.assertEqual(board.get(5, 0), Position(False, False))
        self.assertEqual(board.get(5, 4), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 3)
        self.assertEqual(self.game.n_kittens_p2, 4)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
        Try to promote multiple kittens
    '''
    def test_all_kittens_cheat(self):
        all_units(self.game, False)
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [2, 1], [4, 1] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'invalid_units')

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 9)
        self.assertEqual(board.get(0, 0), Position(False, False))
        self.assertEqual(board.get(2, 1), Position(True, False))
        self.assertEqual(board.get(4, 1), Position(True, False))
        self.assertEqual(board.get(0, 2), Position(True, False))
        self.assertEqual(board.get(4, 2), Position(True, False))
        self.assertEqual(board.get(0, 3), Position(True, False))
        self.assertEqual(board.get(2, 4), Position(True, False))
        self.assertEqual(board.get(4, 4), Position(True, False))
        self.assertEqual(board.get(0, 5), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 0)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 0)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    def test_all_kittens(self):
        all_units(self.game, False)
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [2, 1] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 8)
        self.assertEqual(board.get(0, 0), Position(False, False))
        self.assertEqual(board.get(4, 1), Position(True, False))
        self.assertEqual(board.get(0, 2), Position(True, False))
        self.assertEqual(board.get(4, 2), Position(True, False))
        self.assertEqual(board.get(0, 3), Position(True, False))
        self.assertEqual(board.get(2, 4), Position(True, False))
        self.assertEqual(board.get(4, 4), Position(True, False))
        self.assertEqual(board.get(0, 5), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 0)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 1)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    def test_all_kittens_and_line_promote_line(self):
        all_units(self.game, False, with_line=True)
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [4, 1], [4, 2], [4, 3] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 6)
        self.assertEqual(board.get(2, 1), Position(True, False))
        self.assertEqual(board.get(0, 2), Position(True, False))
        self.assertEqual(board.get(0, 3), Position(True, False))
        self.assertEqual(board.get(2, 4), Position(True, False))
        self.assertEqual(board.get(0, 5), Position(True, False))
        self.assertEqual(board.get(4, 5), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 0)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    def test_all_kittens_and_line_promote_kitten_from_line(self):
        all_units(self.game, False, with_line=True)
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [4, 1] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 8)
        self.assertEqual(board.get(2, 1), Position(True, False))
        self.assertEqual(board.get(0, 2), Position(True, False))
        self.assertEqual(board.get(0, 3), Position(True, False))
        self.assertEqual(board.get(2, 4), Position(True, False))
        self.assertEqual(board.get(0, 5), Position(True, False))
        self.assertEqual(board.get(4, 2), Position(True, False))
        self.assertEqual(board.get(4, 3), Position(True, False))
        self.assertEqual(board.get(4, 5), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 0)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 1)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    def test_all_kittens_and_line_promote_kitten_isolated(self):
        all_units(self.game, False, with_line=True)
        response = self.client.post(
            reverse('core-promote'),
            {
                'game': self.game.id,
                'units': [ [2, 1] ],
            },
            format='json',
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 8)
        self.assertEqual(board.get(0, 2), Position(True, False))
        self.assertEqual(board.get(0, 3), Position(True, False))
        self.assertEqual(board.get(2, 4), Position(True, False))
        self.assertEqual(board.get(0, 5), Position(True, False))
        self.assertEqual(board.get(4, 1), Position(True, False))
        self.assertEqual(board.get(4, 2), Position(True, False))
        self.assertEqual(board.get(4, 3), Position(True, False))
        self.assertEqual(board.get(4, 5), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 0)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 1)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')
