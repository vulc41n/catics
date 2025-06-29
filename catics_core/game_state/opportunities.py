from .promotions import Promotion

class Opportunities:
    def new_column(self):
        pass

    def empty_column(self):
        pass

    def empty_position(self, x: int, y: int):
        pass

    def new_position(self, x: int, y: int):
        pass

    def get_promotions(self) -> list[Promotion]:
        return []

class ColumnOpportunities(Opportunities):
    def __init__(self):
        self.promotions = []
        self.column = 0
    
    def new_column(self):
        self.column = 0

    def empty_position(self, x: int, y: int):
        self.column = 0

    def new_position(self, x: int, y: int):
        self.column += 1
        if self.column == 3:
            self.column = 2
            self.promotions.append((x, y-2))

    def get_promotions(self) -> list[Promotion]:
        return list(map(lambda xy: Promotion([
                (xy[0], xy[1]),
                (xy[0], xy[1]+1),
                (xy[0], xy[1]+2),
            ]), self.promotions))


class LineOpportunities(Opportunities):
    def __init__(self):
        self.promotions = []
        self.lines = [0] * 6

    def empty_column(self):
        self.lines = [0] * 6

    def empty_position(self, x: int, y: int):
        self.lines[y] = 0

    def new_position(self, x: int, y: int):
        self.lines[y] += 1
        if self.lines[y] == 3:
            self.lines[y] = 2
            self.promotions.append((x-2, y))

    def get_promotions(self) -> list[Promotion]:
        return list(map(lambda xy: Promotion([
                (xy[0], xy[1]),
                (xy[0]+1, xy[1]),
                (xy[0]+2, xy[1]),
            ]), self.promotions))

class DiagonalOpportunities(Opportunities):
    def __init__(self):
        self.promotions = []
        self.descending = [0] * 7
        self.ascending = [0] * 7

    def empty_column(self):
        self.descending = [0] * 7
        self.ascending = [0] * 7

    def empty_position(self, x: int, y: int):
        descending_index = x - y + 3
        if 0 <= descending_index < 7:
            self.descending[descending_index] = 0
        ascending_index = x - (5 - y) + 3
        if 0 <= ascending_index < 7:
            self.ascending[ascending_index] = 0

    def new_position(self, x: int, y: int):
        descending_index = x - y + 3
        if 0 <= descending_index < 7:
            self.descending[descending_index] += 1
            if self.descending[descending_index] == 3:
                self.descending[descending_index] = 2
                self.promotions.append(Promotion([
                    (x, y),
                    (x-1, y-1),
                    (x-2, y-2),
                ]))
        ascending_index = x - (5 - y) + 3
        if 0 <= ascending_index < 7:
            self.ascending[ascending_index] += 1
            if self.ascending[ascending_index] == 3:
                self.ascending[ascending_index] = 2
                self.promotions.append(Promotion([
                    (x, y),
                    (x-1, y+1),
                    (x-2, y+2),
                ]))

    def get_promotions(self) -> list[Promotion]:
        return self.promotions
