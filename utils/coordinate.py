class CoordinateParseException(Exception):
    def __init__(self, message, text: str, bounds: bool, split: bool):
        super().__init__(message)
        self.text = text
        self.bounds = bounds
        self.split = split

    def __str__(self):
        return f"Cannot parse {self.text} into a valid coordinate"


class CoordinateClaimedException(Exception):
    def __init__(self, message, x: int, y: int, user: int, end: int):
        super().__init__(message)
        self.x = x,
        self.y = y,
        self.coord = f"({x},{y})"
        self.user = user
        self.end = end

    def __str__(self):
        return f"Coordinate {self.coord} claimed by user {self.user} until {self.end}"


class Coordinate():
    def __init__(self, x, y, user, start, end):
        self.x = x
        self.y = y
        self.user = user
        self.start = start
        self.end = end

    def __str__(self):
        return f"({self.x},{self.y}) - {self.user} - {self.start} - {self.end}"

    def format(self):

        row_format = "**`({:>3},{:>3})`** - `{:>15}`..\n..<t:{:>10}:f> - <t:{:>10}:f>"
        print(row_format.format(*self.__dict__.values()))
        # for team, row in zip(, data):
        #     print(row_format.format(team, *row))
        return row_format.format(*self.__dict__.values())

    @staticmethod
    def parse_coord(coordinate: str) -> [int, int]:
        coords = []
        replacements = str.maketrans({"(": "", ")": "", "[": "", "]": ""})
        coordinate = coordinate.translate(replacements)
        if "," in coordinate:
            coords = [int(x) for x in coordinate.replace(" ", "").split(",")]
        elif ";" in coordinate:
            coords = [int(x) for x in coordinate.replace(" ", "").split(";")]
        elif ":" in coordinate:
            coords = [int(x) for x in coordinate.replace(" ", "").split(":")]
        elif "x" in coordinate:
            coords = [int(x) for x in coordinate.replace(" ", "").split("x")]
        elif " " in coordinate:
            coords = [int(x) for x in coordinate.split(" ")]

        if len(coords) != 2:
            raise CoordinateParseException(
                "Cannot split in two numbers", coordinate, False, True)

        x = coords[0]
        y = coords[1]

        if x < 0 or x > 999 or y < 0 or y > 999:
            raise CoordinateParseException(
                "Coordinate out of bounds", coordinate, True, False)

        return coords

    @classmethod
    def from_string(cls, coordinate, user, start, end):
        x, y = Coordinate.parse_coord(coordinate)
        return cls(x, y, user, start, end)
