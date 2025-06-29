from ..models import Game
from . import Board
from .position import Position
from .counts import Counts
from .exceptions import NoUnitsLeftException, PromotionException
from .promotions import Promotion

class GameState:
    def __init__(self, game: Game):
        self.id = game.id
        self.is_p1_turn= game.is_p1_turn
        self.counts = Counts(
            game.n_kittens_p1,
            game.n_cats_p1,
            game.n_kittens_p2,
            game.n_cats_p2,
        )
        self.board = Board(game.board)
        self.winner = game.winner
        self.promotions = list(map(lambda p: Promotion(p), game.promotions))

    def play(self, x: int, y: int, is_cat: bool):
        if not self.counts.is_sup(self.is_p1_turn, is_cat, 0):
            raise NoUnitsLeftException(is_cat)
        if len(self.promotions) > 0:
            raise PromotionException()

        self.counts += self.board.play(x, y, Position(self.is_p1_turn, is_cat))
        self.counts.add_pieces(self.is_p1_turn, is_cat, -1)
        self.promotions = self.board.look_for_promotions(self.is_p1_turn)

        # no units lefts -> promotion
        # all cats on board -> win
        if self.counts.n_kittens_p1 == 0 and self.counts.n_cats_p1 == 0:
            kittens = self.board.get_all_kittens(True)
            self.promotions.extend(kittens)
            # win!
            if len(kittens) == 0:
                self.winner = '1'
        if self.counts.n_kittens_p2 == 0 and self.counts.n_cats_p2 == 0:
            kittens = self.board.get_all_kittens(False)
            self.promotions.extend(kittens)
            # win!
            if len(kittens) == 0:
                self.winner = '2'

        # if there is only one promotion opportunity, do it
        if len(self.promotions) == 1:
            self.promote(0)

        if len(self.promotions) == 0:
            self.is_p1_turn = not self.is_p1_turn
        # print(self.board)

    def promote(self, promotion_index: int):
        promotion = self.promotions[promotion_index]
        self.promotions = []
        n_cats = 0
        for u in promotion.units:
            n_cats += 1 if self.board.pop(*u).is_cat else 0
        # win !
        if n_cats == 3:
            self.winner = '1' if self.is_p1_turn else '2'
        self.counts.add_pieces(self.is_p1_turn, True, len(promotion.units))

    def save(self):
        Game.objects.filter(id=self.id).update(
            is_p1_turn=self.is_p1_turn,
            n_kittens_p1=self.counts.n_kittens_p1,
            n_cats_p1=self.counts.n_cats_p1,
            n_kittens_p2=self.counts.n_kittens_p2,
            n_cats_p2=self.counts.n_cats_p2,
            winner=self.winner,
            promotions=list(map(lambda p: p.units, self.promotions)),
            board=self.board.value(),
        )

