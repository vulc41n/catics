class Position:
    def __init__(self, is_player1: bool, is_cat: bool):
        self.is_player1 = is_player1
        self.is_cat = is_cat

    def __eq__(self, other) -> bool:
        return isinstance(other, Position) \
            and self.is_player1 == other.is_player1 \
            and self.is_cat == other.is_cat

    def __repr__(self) -> str:
        player = 'p1' if self.is_player1 else 'p2'
        unit = 'c' if self.is_cat else 'k'
        return player + unit

