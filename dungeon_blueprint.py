from collections import deque
from random import randint

class Blueprint:

    def __init__(self, y_axis: int, x_axis: int,
                 alive_players: tuple,
                 item_frequencies: dict):

        self.y_axis = y_axis
        self.x_axis = x_axis
        self.blueprint = self.create_empty_map(y_axis, x_axis)
        self.post_init(alive_players, item_frequencies)

    def post_init(self, alive_players, item_frequencies):
        self.populate_blueprint(alive_players, item_frequencies)


    @staticmethod
    def get_distance(position1: tuple[int], position2: tuple[int]) -> int:
        return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

    @staticmethod
    def create_empty_map(y_axis: int, x_axis: int) -> list[list[str]]:
        return [["." for _ in range(x_axis)] for _ in range(y_axis)]

    def get_position(self, position:tuple):
        return self.blueprint[position[0]][position[1]]

    def spot_is_free(self, position):
        return self.get_position(position) == "."

    def check_for_free_spots(self) -> bool:
        for y in range(self.y_axis):
            for x in range(self.x_axis):
                if self.spot_is_free((y,x)):
                    return True
        return False

    def random_location(self) -> tuple [int, int]:
        return randint(0, self.y_axis - 1), randint(0, self.x_axis - 1)

    def place_single_item(self, item:str, position: tuple) -> None:
        self.blueprint[position[0]],[position[1]] = item

    def populate_blueprint(self, alive_players: tuple, item_frequencies: dict):
        self.place_items_as_group(self.blueprint,
                                  alive_players,
                                  min_dist=1)

        self.place_equal_items(self.blueprint, " ", 1)
        self.place_equal_items(self.blueprint, "o", self.stats.gem_number())

        for key, value in item_frequencies:
            self.place_items(
                self.blueprint,
                item=key,
                frequency=value,
                protected=self.stats.mandatory_items,
            )


    def place_items(self, item: str, frequency=0.1, protected=None) -> None:

        number_of_items = (self.y_axis * self.x_axis) * frequency

        for number in range(int(number_of_items)):
            position = self.random_location()
            if not protected or self.get_position(position) not in protected:
                self.place_single_item(item, position)

    def place_equal_items(self, item: str, number_of_items=1, position=None) -> tuple[int]:

        for number in range(number_of_items):

            while self.check_for_free_spots(self.blueprint):

                if not position or not self.spot_is_free(position):  # if position is taken, generates random location
                    position = self.random_location()

                if self.spot_is_free(position):
                    self.place_single_item(item, position)

                    if number_of_items == 1:
                        return (position[0], position[1])
                    else:
                        break

    @staticmethod
    def place_items_as_group(
            map: list[list[str]],
            items: tuple[str],
            min_dist: int,
            max_dist: int | None = None,
            position: tuple[int] | None = None,
    ):

        items = deque(items)

        initial_position = place_equal_items(map, items.popleft(), position=position)

        placed_positions = [initial_position]
        tested_positions = {initial_position}

        item_to_place = items.popleft() if len(items) > 0 else None
        map_area = len(map) * len(map[0])
        max_dist = min_dist if max_dist is None or max_dist < min_dist else max_dist

        while len(tested_positions) < map_area and item_to_place is not None:

            while True:
                cand_position = location(map)

                if cand_position not in tested_positions:
                    tested_positions.add(cand_position)
                    break

            max_dist_ok = False

            i = 0
            while i < len(placed_positions):

                if get_distance(cand_position, placed_positions[i]) < min_dist:
                    break
                if get_distance(cand_position, placed_positions[i]) <= max_dist:
                    max_dist_ok = True

                if i == len(placed_positions) - 1 and max_dist_ok:
                    placed_positions.append(cand_position)
                    place_equal_items(map, item_to_place, position=cand_position)
                    item_to_place = items.popleft() if len(items) > 0 else None

                i += 1

            if len(tested_positions) == map_area and item_to_place is not None:
                tested_positions = set(placed_positions)

    #CHAT GPT CANDIDATE
    '''def place_items_as_group(
            map: list[list[str]],
            items: tuple[str],
            min_dist: int,
            max_dist: int | None = None,
            position: tuple[int] | None = None,
    ):
        items = deque(items)
        initial_position = place_equal_items(map, items.popleft(), position=position)

        placed_positions = [initial_position]
        tested_positions = {initial_position}

        max_dist = max_dist if max_dist is not None and max_dist >= min_dist else min_dist
        map_area = len(map) * len(map[0])

        while len(tested_positions) < map_area and items:
            cand_position = location(map)

            if cand_position in tested_positions:
                continue

            tested_positions.add(cand_position)

            if any(get_distance(cand_position, pos) < min_dist for pos in placed_positions):
                continue

            if any(min_dist <= get_distance(cand_position, pos) <= max_dist for pos in placed_positions):
                placed_positions.append(cand_position)
                place_equal_items(map, items.popleft(), position=cand_position)

        if items:
            tested_positions = set(placed_positions)'''