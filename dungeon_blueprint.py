from collections import deque
from random import choice
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
            self._generate_empty_layout()

    @staticmethod
    def get_distance(position1: tuple[int, int], position2: tuple[int, int]) -> int:
        """
        Gets the distance between two positions
        :param position1: coordinates of position 1
        :param position2:  coordinates of position 2
        :return: distance between the two positions
        """
        return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

    def _generate_empty_layout(self) -> None:
        """
        Creates an empty grid of points of the specified dimensions
        :return: grid of points
        """
        self.layout = [[self.position_template.copy() for _ in range(self.x_axis)] for _ in range(self.y_axis)]

    def _generate_spot_list(self) -> list[tuple[int, int]]:
        """
        Returns a list of all coordinates of the spots of the grid (y,x)
        :return: list of coordinates
        """
        return [(y, x) for y in range(self.y_axis) for x in range(self.x_axis)]

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
        Checks if the passed positions has an item
        :item: char of the item to check
        :return: True if it has the item, False otherwise
        """
        return self.get_position(position)[get_item_kind(item)] == item

    def has_item_kind(self, position:tuple[int,int], item_kind: str) -> bool:
        """
        Checks if the passed positions has an item of the passed kind
        :item_kind: kind of the item to check
        :return: True if it has the item, False otherwise
        """
        return self.get_position(position)[item_kind] is not None

    def position_is_free(self, position:tuple[int,int]) -> bool:
        """
        Returns True if the value of the given position is "." (free)
        :param position: coordinates of the position
        :return: True if the position is free, False otherwise
        """
        return all(value is None for value in self.get_position(position).values())

    def place_item(self, item:str, position: tuple[int,int]) -> None:
        """
        Places the specified item at the specified position of the map. Overwrites position if not free.
        :param item: item to place
        :param position: coordinates of the position where to place the item
        :return: None
        """
        self.get_position(position)[get_item_kind(item)] = item

    def place_items(self, item: str, number_of_items: int = 1) -> None:
        """
        Places a given number of items in the map. Does not overwrite occupied positions. Items not possible to place
        are skipped
        :param item: item to place
        :param number_of_items: number of items to place
        :return: None
        """
        available_spots: list[tuple[int,int]] = self._generate_spot_list()

        for _ in range(number_of_items):
            if len(available_spots) == 0:
                break
            while len(available_spots) > 0:
                spot: tuple[int,int] = choice(available_spots)
                available_spots.remove(spot)
                if self.position_is_free(spot):
                    self.place_item(item, spot)
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
        available_spots: list[tuple[int,int]] = self._generate_spot_list()

        if position is None:
            position: tuple[int,int] = choice(available_spots)

        self.place_item(items.popleft(), position)
        placed_positions = {position}
        available_spots.remove(position)

        max_dist = max_dist if max_dist is not None and max_dist >= min_dist else min_dist

        while len(available_spots) > 0 and len(items) > 0:
            cand_position = choice(available_spots)
            available_spots.remove(cand_position)

            if not all(min_dist <= self.get_distance(cand_position, p) for p in placed_positions):
                continue

            if not (any(self.get_distance(cand_position, p) <= max_dist for p in placed_positions) if scatter
            else all(self.get_distance(cand_position, p) <= max_dist for p in placed_positions)):
                    continue

            placed_positions.add(cand_position)
            self.place_item(items.popleft(), cand_position)


    def place_items_on_top_shuffled(self, numbers_of_items: dict[str,int], on_top_kind: str,
                                    skip: list[str] | None = None) -> dict[str,int]:
        """
        Places a given number of items in the map in the same position as other items. It places one item of each type
        at the time to avoid placing all the items of a type in a row. Does not overwrite positions occupied by items
        placed by this same method. Items not possible to place are skipped
        :param numbers_of_items: dict containing the item as keys and the number of items to place as value
        :param on_top_kind: number of items to place
        :param skip: list of items chars of items of on_top_kind on which nothing should be placed
        :return: dictionary with the number of items placed
        """
        available_spots = self._generate_spot_list()
        placed_items: dict[str, int] = {item: 0 for item in numbers_of_items}
        total_items = sum(numbers_of_items.values())
        if skip is None:
            skip = []

        for _ in range(total_items):
            for item, number in numbers_of_items.items():
                if placed_items[item] >= number:
                    continue

                while len(available_spots) > 0:
                    spot = choice(available_spots)
                    available_spots.remove(spot)

                    if (self.has_item_kind(spot, on_top_kind)
                            and not self.has_item_kind(spot, get_item_kind(item))
                            and not any(self.has_item(spot, skipped_item) for skipped_item in skip)):
                        self.place_item(item, spot)
                        placed_items[item] += 1
                        break

        return placed_items