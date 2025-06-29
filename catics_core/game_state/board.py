from io import StringIO
from typing import Optional
from .position import Position
from .counts import Counts
from .exceptions import OccupiedException
from .promotions import Promotion
from .opportunities import Opportunities, \
    ColumnOpportunities, \
    LineOpportunities, \
    DiagonalOpportunities

class Board:
    def __init__(self, board: dict[int, dict[int, tuple[bool, bool]]]):
        self.board = {}
        for (x, column) in board.items():
            x = int(x)
            self.board[x] = {}
            for (y, position) in column.items():
                y = int(y)
                self.board[x][y] = Position(position[0], position[1])

    def __len__(self):
        result = 0
        for columns in self.board.values():
            result += len(columns)
        return result

    def __repr__(self) -> str:
        LINE_SEPARATION = '+-----+-----+-----+-----+-----+-----+\n'
        builder = StringIO()
        builder.write('\n')
        builder.write(LINE_SEPARATION)
        for y in range(6):
            for x in range(6):
                builder.write('| ')
                if x not in self.board or y not in self.board[x]:
                    builder.write('    ')
                    continue
                builder.write(str(self.board[x][y]))
                builder.write(' ')
            builder.write('|\n')
            builder.write(LINE_SEPARATION)
        return builder.getvalue()

    def get(self, x: int, y: int) -> Optional[Position]:
        if x not in self.board:
            return None
        if y not in self.board[x]:
            return None
        return self.board[x][y]
        

    def play(self, x: int, y: int, position: Position) -> Counts:
        fallen = Counts()
        if x not in self.board:
            self.board[x] = {}
        elif y in self.board[x]:
            raise OccupiedException()
        self.board[x][y] = position

        # push neighbors
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                if y_offset == 0 and x_offset == 0:
                    continue

                x_neighbor = x + x_offset
                y_neighbor = y + y_offset
                if x_neighbor not in self.board or y_neighbor not in self.board[x_neighbor]:
                    continue

                x_new = x_neighbor + x_offset
                y_new = y_neighbor + y_offset

                # blocked by another unit
                if x_new in self.board and y_new in self.board[x_new]:
                    continue

                # kitten blocked by a cat
                if not position.is_cat and self.board[x_neighbor][y_neighbor].is_cat:
                    continue

                # take pushed
                pushed = self.pop(x_neighbor, y_neighbor)

                # fall
                if not (0 <= x_new < 6 and 0 <= y_new < 6):
                    fallen.add_pieces(pushed.is_player1, pushed.is_cat, 1)
                    continue

                # put pushed
                if x_new not in self.board:
                    self.board[x_new] = {}
                self.board[x_new][y_new] = pushed

        return fallen

    def pop(self, x: int, y: int) -> Position:
        result = self.board[x].pop(y)
        if len(self.board[x]) == 0:
            del self.board[x]
        return result

    def look_for_promotions(self, is_player1: bool) -> list[Promotion]:
        promotions = Counts()
        opportunities: list[Opportunities] = [
            ColumnOpportunities(),
            LineOpportunities(),
            DiagonalOpportunities(),
        ]

        for x in range(6):
            if x not in self.board:
                for o in opportunities:
                    o.empty_column()
                continue
            for o in opportunities:
                o.new_column()
            for y in range(6):
                if y not in self.board[x] or self.board[x][y].is_player1 != is_player1:
                    for o in opportunities:
                        o.empty_position(x, y)
                    continue
                for o in opportunities:
                    o.new_position(x, y)

        promotions = []
        for (i, o) in enumerate(opportunities):
            promotions.extend(o.get_promotions())

        return promotions

    def get_all_kittens(self, is_player1: bool) -> list[Promotion]:
        promotions = []
        for (x, column) in self.board.items():
            for (y, position) in self.board[x].items():
                if position.is_player1 != is_player1 or position.is_cat:
                    continue
                promotions.append(Promotion([(x, y)]))
        return promotions

    def value(self) -> dict[int, dict[int, tuple[bool, bool]]]:
        value = {}
        for (x, column) in self.board.items():
            value[x] = {}
            for (y, position) in column.items():
                value[x][y] = [position.is_player1, position.is_cat]
        return value
        
