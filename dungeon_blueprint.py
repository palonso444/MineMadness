from collections import deque
from random import randint
from items_kinds import get_item_kind


class Blueprint:
    """
    Program-agnostic module to generate ASCII-based blueprints of dungeon rooms.
    Supports multiple item kinds per position
    """

    def __init__(self, y_axis: int | None = None, x_axis: int | None = None, layout:list[list] | None = None):

        if layout is None and (y_axis is None or x_axis is None):
            raise ValueError("No None allowed in y_axis and x_axis if layout is None.")

        self.position_template: dict[str, str | None] = {
                                                            "player": None,
                                                            "monster": None,
                                                            "trap": None,
                                                            "wall": None,
                                                            "pickable": None,
                                                            "treasure": None,
                                                            "exit": None
                                                        }
        self.layout: list[list] | None = layout
        if x_axis is not None and y_axis is not None:
            self.y_axis: int = y_axis
            self.x_axis: int = x_axis
        else:
            self.y_axis: int = len(layout)
            self.x_axis: int = len(layout[0])
        self.area: int = self.y_axis * self.x_axis

        self.post_init()

    def post_init(self) -> None:
        """
        This is defined as post_init because it needs self.position_template to be initialized
        """
        if self.layout is None:
            self.layout: list[list[dict]] = self.generate_empty_layout(self.y_axis, self.x_axis)

    @staticmethod
    def get_distance(position1: tuple[int, int], position2: tuple[int, int]) -> int:
        """
        Gets the distance between two positions
        :param position1: coordinates of position 1
        :param position2:  coordinates of position 2
        :return: distance between the two positions
        """
        return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

    def generate_empty_layout(self, y_axis: int, x_axis: int) -> list[list[dict]]:
        """
        Creates an empty grid of points of the specified dimensions
        :param y_axis: length of the y-axis
        :param x_axis: length of the x-axis
        :return: grid of points
        """
        return [[self.position_template.copy() for _ in range(x_axis)] for _ in range(y_axis)]

    def to_dict(self) -> dict:
        """
        Converts the instance of the class to a dictionary
        :return: dictionary containing all attributes of the instance and their values
        """
        return{key: value for key, value in vars(self).items()}

    def get_position(self, position:tuple[int,int]) -> dict:
        """
        Returns the value of the specified position of the grid
        :param position: coordinates of the position whose value must be returned
        :return: contents of the specified position
        """
        return self.layout[position[0]][position[1]]

    def has_item(self, position:tuple[int,int], item: str) -> bool:
        """
        Checks if the passed positions has an item of the passed kind
        :item: char of the item to check
        :return: True if it has the item, False otherwise
        """
        return self.get_position(position)[get_item_kind(item)] == item

    def spot_is_free(self, position:tuple[int,int]) -> bool:
        """
        Returns True if the value of the given position is "." (free)
        :param position: coordinates of the position
        :return: True if the position is free, False otherwise
        """
        return all(value is None for value in self.get_position(position).values())

    def check_if_free_spots(self) -> bool:
        """
        Checks if any position of the grid has a value of "." (free)
        :return: True if there is at least one free position, False otherwise
        """
        return any(self.spot_is_free((y, x)) for y in range(self.y_axis) for x in range(self.x_axis))

    def get_random_position(self) -> tuple [int, int]:
        """
        Returns a random position of the grid
        :return: coordinates of the random position
        """
        return randint(0, self.y_axis - 1), randint(0, self.x_axis - 1)

    def place_single_item(self, item:str, position: tuple[int,int]) -> None:
        """
        Places the specified item at the specified position of the map. Overwrites position if not free.
        :param item: item to place
        :param position: coordinates of the position where to place the item
        :return: None
        """
        self.get_position(position)[get_item_kind(item)] = item

    def place_items(self, item: str, number_of_items = 1) -> None:
        """
        Places a given number of items in the map. Does not overwrite occupied positions.
        :param item: item to place
        :param number_of_items: number of items to place
        :return: None
        """
        for number in range(number_of_items):

            while self.check_if_free_spots():
                position = self.get_random_position()

                if self.spot_is_free(position):
                    self.place_single_item(item, position)
                    break

    def place_items_as_group(self, items: list, min_dist: int, max_dist: int | None = None,
                             position: tuple[int, int] | None = None, scatter:bool = True) -> None:
        """
        Places items grouped between a minimum and maximum distance. Items not possible to place between specified
        distances are skipped.
        :param items: tuple containing the items to place grouped
        :param min_dist: minimum distance to be kept between ALL items
        :param max_dist: maximum distance to be kept between items
        :param position: position of the first item placed. If not specified, random position is generated
        :param scatter: if set to True, max_dist is required only to one of the items placed, resulting in a more
        scattered positioning but guarantees that all items are placed in most of the cases.
        :return: None
        """

        items = deque(items)
        if position is None:
            position = self.get_random_position()

        self.place_single_item(items.popleft(), position=position)
        placed_positions = {position}
        tested_positions = {position}
        max_dist = max_dist if max_dist is not None and max_dist >= min_dist else min_dist

        while len(tested_positions) < self.area and len(items) > 0:
            cand_position = self.get_random_position()

            if cand_position in tested_positions:
                continue

            tested_positions.add(cand_position)

            if all(min_dist <= self.get_distance(cand_position, position) for position in placed_positions):

                if ((scatter and any (self.get_distance(cand_position, position) <= max_dist
                                      for position in placed_positions)) or
                        (not scatter and all(self.get_distance(cand_position, position) <= max_dist
                                             for position in placed_positions))):

                    placed_positions.add(cand_position)
                    self.place_single_item(items.popleft(), position=cand_position)

if __name__ == "__main__":

    test = Blueprint(10,10)
    #test.place_single_item("%", (1,1))
    #test.place_items("4", 0.5)
    #test.place_equal_items("2",99)
    #test.place_items_as_group(("A","B","C", "D", "E"),1, 2, scatter=True)
