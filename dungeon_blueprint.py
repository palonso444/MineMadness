from collections import deque
from random import randint


class Blueprint:
    """
    Program-agnostic module to generate ASCII-based blueprints of dungeon rooms
    """

    def __init__(self, y_axis: int | None = None, x_axis: int | None = None, layout:list[list] | None = None):

        if layout is None and (y_axis is None or x_axis is None):
            raise ValueError("No None allowed in y_axis and x_axis if layout is None.")

        if x_axis is not None and y_axis is not None:
            self.y_axis: int = y_axis
            self.x_axis: int = x_axis
        else:
            self.y_axis: int = len(layout)
            self.x_axis: int = len(layout[0])
        self.area: int = self.y_axis * self.x_axis

        if layout is None:
            self.layout: list[list[str]] = self.generate_empty_layout(y_axis, x_axis)
        else:
            self.layout: list[list[str]] = layout

    @staticmethod
    def get_distance(position1: tuple[int, int], position2: tuple[int, int]) -> int:
        """
        Gets the distance between two positions
        :param position1: coordinates of position 1
        :param position2:  coordinates of position 2
        :return: distance between the two positions
        """
        return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

    @staticmethod
    def generate_empty_layout(y_axis: int, x_axis: int) -> list[list[str]]:
        """
        Creates an empty grid of points of the specified dimensions
        :param y_axis: length of the y-axis
        :param x_axis: length of the x-axis
        :return: grid of points
        """
        return [["." for _ in range(x_axis)] for _ in range(y_axis)]

    def to_dict(self) -> dict:
        """
        Converts the instance of the class to a dictionary
        :return: dictionary containing all attributes of the instance and their values
        """
        return{key: value for key, value in vars(self).items()}

    def get_position(self, position:tuple[int,int]) -> str:
        """
        Returns the value of the specified position of the grid
        :param position: coordinates of the position whose value must be returned
        :return: value of the specified position
        """
        return self.layout[position[0]][position[1]]

    def spot_is_free(self, position:tuple[int,int]) -> bool:
        """
        Returns True if the value of the given position is "." (free)
        :param position: coordinates of the position
        :return: True if the position is free, False otherwise
        """
        return self.get_position(position) == "."

    def check_for_free_spots(self) -> bool:
        """
        Checks if any position of the grid has a value of "." (free)
        :return: True if there is at least one free position, False otherwise
        """
        return any(self.spot_is_free((y, x)) for y in range(self.y_axis) for x in range(self.x_axis))

    def random_location(self) -> tuple [int, int]:
        """
        Returns a random position of the grid
        :return: coordinates of the random position
        """
        return randint(0, self.y_axis - 1), randint(0, self.x_axis - 1)

    def print_layout(self) -> None:
        """
        Prints the room grid in a pretty and legible way
        :return: None
        """
        for row in self.layout:
            print(" ".join(row))

    def place_single_item(self, item:str, position: tuple[int,int]) -> None:
        """
        Places the specified item at the specified position of the map. Overwrites position if not free.
        :param item: item to place
        :param position: coordinates of the position where to place the item
        :return: None
        """
        self.layout[position[0]][position[1]] = item

    def place_items(self, item: str, number_of_items = 1) -> None:
        """
        Places a given number of items in the map. Does not overwrite occupied positions.
        :param item: item to place
        :param number_of_items: number of items to place
        :return: None
        """
        for number in range(number_of_items):

            while self.check_for_free_spots():
                position = self.random_location()

                if self.spot_is_free(position):
                    self.place_single_item(item, position)
                    break

    def place_items_as_group(self, items: tuple, min_dist: int, max_dist: int | None = None,
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
            position = self.random_location()

        self.place_single_item(items.popleft(), position=position)
        placed_positions = {position}
        tested_positions = {position}
        max_dist = max_dist if max_dist is not None and max_dist >= min_dist else min_dist

        while len(tested_positions) < self.area and len(items) > 0:
            cand_position = self.random_location()

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

    def purge_blueprint(self, max_total_frequency:float, protected: set | None = None) -> None:
        """
        Cleans the blueprint until the max_frequency is reached to avoid overcrowding
        :param max_total_frequency: max sum frequencies of all items allowed
        :param protected: items that must be kept
        :return: None
        """
        if protected is None:
            protected = {"."}
        else:
            protected.add(".")

        max_occupied_tiles = self.area * max_total_frequency
        current_occupied_tiles = sum(len([item for item in row if item != "."]) for row in self.layout)

        while current_occupied_tiles > max_occupied_tiles:
            if all(item in protected for row in self.layout for item in row):
                break
            position = self.random_location()
            if self.get_position(position) not in protected:
                self.place_single_item(".", position)
                current_occupied_tiles = sum(len([item for item in row if item != "."]) for row in self.layout)


if __name__ == "__main__":

    test = Blueprint(10,10)
    #test.place_single_item("%", (1,1))
    #test.place_items("4", 0.5)
    #test.place_equal_items("2",99)
    #test.place_items_as_group(("A","B","C", "D", "E"),1, 2, scatter=True)
    test.print_layout()
