class Counts:
    def __init__(
        self,
        n_kittens_p1: int = 0,
        n_cats_p1: int = 0,
        n_kittens_p2: int = 0,
        n_cats_p2: int = 0,
    ):
        self.n_kittens_p1 = n_kittens_p1
        self.n_cats_p1 = n_cats_p1
        self.n_kittens_p2 = n_kittens_p2
        self.n_cats_p2 = n_cats_p2

    def __add__(self, other):
        return Counts(
            self.n_kittens_p1 + other.n_kittens_p1,
            self.n_cats_p1 + other.n_cats_p1,
            self.n_kittens_p2 + other.n_kittens_p2,
            self.n_cats_p2 + other.n_cats_p2,
        )

    def add_pieces(self, is_player1: bool, is_cat: bool, value: int):
        if is_player1:
            if is_cat:
                self.n_cats_p1 += value
            else:
                self.n_kittens_p1 += value
        else:
            if is_cat:
                self.n_cats_p2 += value
            else:
                self.n_kittens_p2 += value

    def is_sup(self, is_player1: bool, is_cat: bool, value: int) -> bool:
        if is_player1:
            if is_cat:
                return self.n_cats_p1 > value
            return self.n_kittens_p1 > value
        if is_cat:
            return self.n_cats_p2 > value
        return self.n_kittens_p2 > value
