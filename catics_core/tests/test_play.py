from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from catics_auth.models import Validation
from ..game_state import GameState, Board, Position
from .helpers import two_players_setup, all_units, PASSWORD

User = get_user_model()

class PlayTestCase(APITestCase):
    def setUp(self):
        two_players_setup(self)

    def test_unlogged(self):
        self.client.credentials()
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'].code, 'not_authenticated')
        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 0)

    def test_unvalidated(self):
        Validation.objects.filter(user=self.player1).update(is_validated=False)

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'].code, 'unvalidated')

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 0)

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |*p1k*|     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_empty_board(self):
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(3, 3), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 7)

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |*p2k*|     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     | p1k |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_push_kitten_kitten_diagonal(self):
        state = GameState(self.game)
        state.play(3, 3, False)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 2, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(2, 2), Position(False, False))
        self.assertEqual(board.get(4, 4), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 7)
        self.assertEqual(self.game.n_kittens_p2, 7)

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1k |*p2k*|     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_push_kitten_kitten_horizontal(self):
        state = GameState(self.game)
        state.play(2, 2, False)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 2, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(3, 2), Position(False, False))
        self.assertEqual(board.get(1, 2), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 7)
        self.assertEqual(self.game.n_kittens_p2, 7)

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1k |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |*p2k*|     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_push_kitten_kitten_vertical(self):
        state = GameState(self.game)
        state.play(2, 2, False)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(2, 3), Position(False, False))
        self.assertEqual(board.get(2, 1), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 7)
        self.assertEqual(self.game.n_kittens_p2, 7)

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p2k |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1k |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |*p2k*|     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     | p1k |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_block_kitten_kitten_diagonal(self):
        state = GameState(self.game)
        state.play(2, 2, False)
        state.play(1, 1, False)
        state.play(4, 4, False)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 4)
        self.assertEqual(board.get(1, 1), Position(False, False))
        self.assertEqual(board.get(2, 2), Position(True, False))
        self.assertEqual(board.get(3, 3), Position(False, False))
        self.assertEqual(board.get(5, 5), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 6)
        self.assertEqual(self.game.n_kittens_p2, 6)

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |*p2k*|     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     | p1c |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_block_kitten_cat(self):
        # give one cat to player 1
        self.game.n_cats_p1 += 1
        self.game.n_kittens_p1 -= 1

        state = GameState(self.game)
        state.play(3, 3, True)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 2, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(2, 2), Position(False, False))
        self.assertEqual(board.get(3, 3), Position(True, True))
        self.assertEqual(self.game.n_kittens_p1, 7)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 0)
        self.assertEqual(self.game.n_cats_p2, 0)

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |*p2c*|     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     | p1c |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_push_cat_cat(self):
        # give one cat to both players
        self.game.n_cats_p1 += 1
        self.game.n_kittens_p1 -= 1
        self.game.n_cats_p2 += 1
        self.game.n_kittens_p2 -= 1

        state = GameState(self.game)
        state.play(3, 3, True)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 2, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(2, 2), Position(False, True))
        self.assertEqual(board.get(4, 4), Position(True, True))
        self.assertEqual(self.game.n_kittens_p1, 7)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 0)
        self.assertEqual(self.game.n_cats_p2, 0)


    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |*p2c*|     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     | p1k |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_push_cat_kitten(self):
        # give one cat to player 2
        self.game.n_cats_p2 += 1
        self.game.n_kittens_p2 -= 1

        state = GameState(self.game)
        state.play(3, 3, False)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 2, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(2, 2), Position(False, True))
        self.assertEqual(board.get(4, 4), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 7)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 0)
        self.assertEqual(self.game.n_cats_p2, 0)

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     | p2c |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |*p1c*| p2k |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     | p1k | p1c | p2k |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_fall_bottom_right(self):
        self.game.n_kittens_p1 = 5
        self.game.n_cats_p1 = 1
        self.game.n_kittens_p2 = 5
        self.game.board = {
            3: { 5: [False, True] },
            4: { 5: [False, False] },
            5: { 3: [True, False], 4: [True, True], 5: [False, False] },
        }
        self.game.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 4, 'y': 4, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(4, 4), Position(True, True))
        self.assertEqual(self.game.n_kittens_p1, 6)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 1)
        self.assertEqual(self.game.n_cats_p2, 1)


    '''
    +-----+-----+-----+-----+-----+-----+
    | p2k | p2k | p2c |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p1c |*p1c*|     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p1k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_fall_top_left(self):
        self.game.n_kittens_p1 = 5
        self.game.n_cats_p1 = 1
        self.game.n_kittens_p2 = 5
        self.game.board = {
            0: { 0: [False, False], 1: [False, False], 2: [False, True] },
            1: { 0: [True, True] },
            2: { 0: [True, False] },
        }
        self.game.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 1, 'y': 1, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(1, 1), Position(True, True))
        self.assertEqual(self.game.n_kittens_p1, 6)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 1)
        self.assertEqual(self.game.n_cats_p2, 1)

    def test_occupied(self):
        state = GameState(self.game)
        state.play(3, 3, False)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'occupied')

    def test_no_cats(self):
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'no_units_left')

    def test_no_kittens(self):
        self.game.n_kittens_p1 = 0
        self.game.n_cats_p1 = 8
        self.game.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'no_units_left')

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p1k |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1k |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |*p1k*|     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     | p2k |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_diagonal1_kittens(self):
        state = GameState(self.game)
        state.play(2, 2, False)
        state.play(5, 5, False)
        state.play(3, 3, False)
        state.play(4, 4, False)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(5, 5), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p1c |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1k |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |*p1k*|     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     | p2k |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_diagonal1_mixed(self):
        # give one cat to player 1
        self.game.n_cats_p1 += 1
        self.game.n_kittens_p1 -= 1

        state = GameState(self.game)
        state.play(1, 1, True)
        state.play(5, 5, False)
        state.play(2, 2, False)
        state.play(4, 4, False)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(5, 5), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p1c |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1c |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |*p1c*|     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     | p2c |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_diagonal1_cats(self):
        # give cats to both players
        self.game.n_cats_p1 += 3
        self.game.n_kittens_p1 -= 3
        self.game.n_cats_p2 += 2
        self.game.n_kittens_p2 -= 2

        state = GameState(self.game)
        state.play(2, 2, True)
        state.play(5, 5, True)
        state.play(3, 3, True)
        state.play(4, 4, True)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(5, 5), Position(False, True))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 6)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 1)
        self.assertEqual(self.game.winner, '1')

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     | p1k |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     | p1k |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |*p1k*|     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p2k |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_diagonal2_kittens(self):
        state = GameState(self.game)
        state.play(3, 2, False)
        state.play(0, 5, False)
        state.play(2, 3, False)
        state.play(1, 4, False)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(0, 5), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     | p2k |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |*p1k*|     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1k |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p1c |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_diagonal2_mixed(self):
        # give one cat to player 1
        self.game.n_cats_p1 += 1
        self.game.n_kittens_p1 -= 1

        state = GameState(self.game)
        state.play(1, 4, True)
        state.play(5, 0, False)
        state.play(2, 3, False)
        state.play(4, 1, False)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 2, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(5, 0), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     | p1c |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     | p1c |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |*p1c*|     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p2c |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_diagonal2_cats(self):
        # give cats to both players
        self.game.n_cats_p1 += 3
        self.game.n_kittens_p1 -= 3
        self.game.n_cats_p2 += 2
        self.game.n_kittens_p2 -= 2

        state = GameState(self.game)
        state.play(3, 2, True)
        state.play(0, 5, True)
        state.play(2, 3, True)
        state.play(1, 4, True)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 3, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(0, 5), Position(False, True))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 6)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 1)
        self.assertEqual(self.game.winner, '1')

    '''
    +-----+-----+-----+-----+-----+-----+
    | p1k | p1k |*p1k*| p2k |     | p2k |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_horizontal_kittens(self):
        state = GameState(self.game)
        state.play(1, 0, False)
        state.play(5, 0, False)
        state.play(2, 0, False)
        state.play(3, 0, False)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 0, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(5, 0), Position(False, False))
        self.assertEqual(board.get(4, 0), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 6)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
    +-----+-----+-----+-----+-----+-----+
    | p1c | p1k |*p1k*|     | p2k |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_horizontal_mixed(self):
        # give one cat to player 1
        self.game.n_cats_p1 += 1
        self.game.n_kittens_p1 -= 1

        state = GameState(self.game)
        state.play(0, 0, True)
        state.play(5, 0, False)
        state.play(1, 0, False)
        state.play(4, 0, False)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 0, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(4, 0), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
    +-----+-----+-----+-----+-----+-----+
    | p1c | p1c |*p1c*| p2c |     | p2c |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_horizontal_cats(self):
        # give cats to both players
        self.game.n_cats_p1 += 3
        self.game.n_kittens_p1 -= 3
        self.game.n_cats_p2 += 2
        self.game.n_kittens_p2 -= 2

        state = GameState(self.game)
        state.play(1, 0, True)
        state.play(5, 0, True)
        state.play(2, 0, True)
        state.play(3, 0, True)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 2, 'y': 0, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(5, 0), Position(False, True))
        self.assertEqual(board.get(4, 0), Position(False, True))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 6)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, '1')


    '''
    +-----+-----+-----+-----+-----+-----+
    | p1k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p1k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |*p1k*|     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p2k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p2k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_vertical_kittens(self):
        state = GameState(self.game)
        state.play(0, 1, False)
        state.play(0, 5, False)
        state.play(0, 2, False)
        state.play(0, 3, False)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 0, 'y': 2, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(0, 5), Position(False, False))
        self.assertEqual(board.get(0, 4), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 6)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
    +-----+-----+-----+-----+-----+-----+
    | p1c |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p1k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |*p1k*|     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p2k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_vertical_mixed(self):
        # give one cat to player 1
        self.game.n_cats_p1 += 1
        self.game.n_kittens_p1 -= 1

        state = GameState(self.game)
        state.play(0, 0, True)
        state.play(0, 5, False)
        state.play(0, 1, False)
        state.play(0, 4, False)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 0, 'y': 2, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 1)
        self.assertEqual(board.get(0, 4), Position(False, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 7)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    '''
    +-----+-----+-----+-----+-----+-----+
    | p1c |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p1c |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |*p1c*|     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p2c |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    | p2c |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_line_vertical_cats(self):
        # give cats to both players
        self.game.n_cats_p1 += 3
        self.game.n_kittens_p1 -= 3
        self.game.n_cats_p2 += 2
        self.game.n_kittens_p2 -= 2

        state = GameState(self.game)
        state.play(0, 1, True)
        state.play(0, 5, True)
        state.play(0, 2, True)
        state.play(0, 3, True)
        state.save()

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 0, 'y': 2, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 2)
        self.assertEqual(board.get(0, 5), Position(False, True))
        self.assertEqual(board.get(0, 4), Position(False, True))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 6)
        self.assertEqual(self.game.n_cats_p1, 3)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, '1')

    '''
    +-----+-----+-----+-----+-----+-----+
    | p2k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1k |     | p1k |     |
    +-----+-----+-----+-----+-----+-----+
    | p1k |     |     |     | p1k |     |
    +-----+-----+-----+-----+-----+-----+
    | p1k |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1k |     | p1k |     |
    +-----+-----+-----+-----+-----+-----+
    |*p1k*|     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_all_kittens(self):
        all_units(self.game, False, skip_last_move=True)

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 0, 'y': 5, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)
        board_data = response.data['board']

        # player 2 can't play because player 1 has to choose which kitten will be promoted
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 2, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'not_your_turn')

        self.game.refresh_from_db()
        board = Board(board_data)
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

    '''
    +-----+-----+-----+-----+-----+-----+
    | p2c |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1c |     | p1c |     |
    +-----+-----+-----+-----+-----+-----+
    | p1c |     |     |     | p1c |     |
    +-----+-----+-----+-----+-----+-----+
    | p1c |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1c |     | p1c |     |
    +-----+-----+-----+-----+-----+-----+
    |*p1c*|     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_all_cats(self):
        # cats only
        self.game.n_cats_p1 += 8
        self.game.n_kittens_p1 -= 8
        self.game.n_cats_p2 += 8
        self.game.n_kittens_p2 -= 8

        all_units(self.game, True, skip_last_move=True)

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 0, 'y': 5, 'is_cat': True },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
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
        self.assertEqual(self.game.n_kittens_p1, 0)
        self.assertEqual(self.game.n_kittens_p2, 0)
        self.assertEqual(self.game.n_cats_p1, 0)
        self.assertEqual(self.game.n_cats_p2, 7)
        self.assertEqual(self.game.winner, '1')

    '''
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p2c |     |     |     | p2c |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     |     |*p2k*|     |
    +-----+-----+-----+-----+-----+-----+
    |     |     |     | p1c |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     |     | p1c |     |     |     |
    +-----+-----+-----+-----+-----+-----+
    |     | p2c |     |     |     | p1k |
    +-----+-----+-----+-----+-----+-----+
    '''
    def test_2_players_line(self):
        self.game.n_cats_p1 += 2
        self.game.n_kittens_p1 -= 2
        self.game.n_cats_p2 += 3
        self.game.n_kittens_p2 -= 3

        state = GameState(self.game)
        state.play(0, 0, False)
        state.play(1, 1, True)
        state.play(2, 4, True)
        state.play(1, 5, True)
        state.play(4, 2, True)
        state.play(5, 1, True)
        state.play(5, 5, False)
        state.save()

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 4, 'y': 2, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 200)

        self.game.refresh_from_db()
        board = Board(response.data['board'])
        self.assertEqual(len(board), 7)
        self.assertEqual(board.get(1, 1), Position(False, True))
        self.assertEqual(board.get(5, 1), Position(False, True))
        self.assertEqual(board.get(4, 2), Position(False, False))
        self.assertEqual(board.get(3, 3), Position(True, True))
        self.assertEqual(board.get(2, 4), Position(True, True))
        self.assertEqual(board.get(1, 5), Position(False, True))
        self.assertEqual(board.get(5, 5), Position(True, False))
        self.assertEqual(self.game.n_kittens_p1, 5)
        self.assertEqual(self.game.n_kittens_p2, 4)
        self.assertEqual(self.game.n_cats_p1, 0)
        self.assertEqual(self.game.n_cats_p2, 0)
        self.assertEqual(self.game.winner, 'n')

    def test_wrong_player(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token2)
        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'].code, 'not_your_turn')

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 0)

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
            is_validated=True,
        )
        response = self.client.post(
            reverse('auth-login'),
            { 'username': 'other', 'password': PASSWORD },
        )
        self.client.credentials(HTTP_AUTHORIZATION="Token " + response.data['token'])

        response = self.client.post(
            reverse('core-play'),
            { 'game': self.game.id, 'x': 3, 'y': 3, 'is_cat': False },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data['detail'].code, 'not_a_player')

        self.game.refresh_from_db()
        board = Board(self.game.board)
        self.assertEqual(len(board), 0)

