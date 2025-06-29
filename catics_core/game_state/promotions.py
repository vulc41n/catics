
class Promotion:
    def __init__(self, units: list[tuple[int, int]]):
        self.units = units

    def __repr__(self) -> str:
        return 'Promotion{}'.format(self.units)
