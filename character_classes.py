from random import randint
from abc import ABC, abstractmethod

import crapgeon_utils as utils
import tile_classes as tiles
import game_stats as stats


class Character(ABC):

    @classmethod
    def rearrange_ids(cls) -> None:

        for character in cls.data:
            character.id = cls.data.index(character)

    @classmethod
    def reset_moves(cls) -> None:

        for character in cls.data:
            character.stats.remaining_moves = character.stats.moves

    # INSTANCE METHODS

    def __init__(self):

        self.name: str | None = None
        self.inventory: dict | None = None
        self.id: int | None = None
        self.position: tuple | None = None

        self.token = None
        self.dungeon = None

    def update_position(self, position: tuple[int]) -> None:

        self.__class__.data[self.id].position = position

    def fight_on_tile(self, opponent_tile: tiles.Tile) -> None:

        opponent = opponent_tile.get_character()
        game = self.dungeon.game

        damage = randint(self.stats.strength[0], self.stats.strength[1])
        if isinstance(self, Player) and self.stats.weapons > 0:
            self.stats.weapons -= 1
            game.update_switch("weapons")
            if self.stats.armed_strength_incr is not None:
                damage += self.stats.armed_strength_incr

        opponent._apply_thoughness(damage)

        if opponent.stats.thoughness < 0:
            opponent.stats.health += (
                opponent.stats.thoughness
            )  # thoughness is negative now

        self.stats.remaining_moves -= 1

        if opponent.stats.health <= 0:
            opponent._kill_character(opponent_tile)

        self.dungeon.show_damage_token(
            opponent.token.shape.pos, opponent.token.shape.size
        )

    def has_moved(self) -> bool:

        if self.stats.remaining_moves == self.stats.moves:
            return False
        return True

    def _apply_thoughness(self, damage):

        self.stats.thoughness -= damage

    def _kill_character(self, tile):

        self.__class__.data.remove(self)
        self.__class__.rearrange_ids()
        tile.clear_token(self.token.kind)

    # MOVEMENT METHODS TO IMPLEMENT

    def glide(self):
        raise NotImplementedError()

    def walk(self):
        raise NotImplementedError()

    def stomp(self):
        raise NotImplementedError()


class Player(Character, ABC):

    player_chars: tuple = ("%", "?", "&")  # % sawyer, ? hawkins, & crusher jane
    data: list = list()
    exited: set = set()
    gems: int = 0

    @classmethod
    def transfer_player(cls, name: str) -> Character:

        for player in cls.exited:
            if player.name == name:
                return player

    @classmethod
    def remove_effects(cls, turn: int) -> None:

        for character in cls.data:
            for attribute, effects in character.effects.items():

                i = 0
                while i < len(effects):

                    if effects[i]["end_turn"] == turn:
                        player_stat = getattr(character.stats, attribute)

                        if isinstance(player_stat, int):
                            new_value = player_stat - effects[i]["size"]
                        elif isinstance(player_stat, tuple):
                            new_value = (
                                player_stat[0],
                                player_stat[1] - effects[i]["size"],
                            )

                        effects.remove(effects[i])
                        setattr(character.stats, attribute, new_value)
                        continue
                    i += 1

    # INSTANCE METHODS

    def __init__(self):
        super().__init__()
        self.kind: str = "player"
        self.blocked_by: tuple = ("wall", "monster")
        self.cannot_share_tile_with: tuple = ("wall", "monster", "player")
        self.free_actions: tuple = (None,)
        self.ignores: tuple = (None,)
        self.inventory: dict[str:int] = {
            "jerky": 0,
            "coffee": 0,
            "tobacco": 0,
            "whisky": 0,
            "talisman": 0,
        }
        self.effects: dict[str:list] = {"moves": [], "thoughness": [], "strength": []}
        self.state: str | None = None

    def get_movement_range(
        self, dungeon_layout
    ):  # TODO: DO NOT ACTIVATE IF WALLS ARE PRESENT
        # TODO: better as method of Player Class

        mov_range = set()  # set of tuples (no repeated values)
        remaining_moves = self.stats.remaining_moves

        # GET CURRENT PLAYER POSITION
        mov_range.add((self.position[0], self.position[1]))

        for move in range(
            1, remaining_moves + 1
        ):  # starts at 1 not to include current player position again

            # INCLUDE ALL POSSIBLE MOVES ON THE SAME ROW AS PLAYER
            self._get_lateral_range(self.position[0], move, mov_range, dungeon_layout)
            remaining_moves -= 1

            if self.position[0] - move >= 0:  # if height within range up

                # INCLUDE ALL POSSIBLE MOVES DIRECTION UP
                mov_range.add(
                    (self.position[0] - move, self.position[1])
                )  # one step up.

                for side_move in range(1, remaining_moves + 1):  # one step both sides

                    self._get_lateral_range(
                        self.position[0] - move,
                        side_move,
                        mov_range,
                        dungeon_layout,
                    )

            if (
                self.position[0] + move < dungeon_layout.rows
            ):  # if height within range down

                # INCLUDE ALL POSSIBLE MOVES DIRECTION DOWN
                mov_range.add(
                    (self.position[0] + move, self.position[1])
                )  # one step down.

                for side_move in range(1, remaining_moves + 1):  # one step both sides

                    self._get_lateral_range(
                        self.position[0] + move,
                        side_move,
                        mov_range,
                        dungeon_layout,
                    )

        return mov_range

    def pick_object(self, tile: tiles.Tile) -> None:

        game = self.dungeon.game

        # if tile.token.species not in self.ignores:
        if (
            tile.token.kind not in self.ignores
            and tile.token.species not in self.ignores
        ):

            if tile.token.species == "gem":
                Player.gems += 1
                game.update_switch("gems")

            elif tile.token.species in self.inventory.keys():
                self.inventory[tile.token.species] += 1
                game.inv_object = tile.token.species

            else:
                character_attribute = getattr(self.stats, tile.token.species + "s")
                character_attribute += 1
                setattr(self.stats, tile.token.species + "s", character_attribute)
                game.update_switch(tile.token.species + "s")

            tile.clear_token(tile.token.kind)

    def dig(self, wall_tile: tiles.Tile) -> None:

        game = self.dungeon.game

        if self.stats.shovels > 0:
            self.stats.shovels -= 1
            game.update_switch("shovels")
        self.stats.remaining_moves -= self.stats.digging_moves

        self.dungeon.show_digging_token(
            wall_tile.token.shape.pos, wall_tile.token.shape.size
        )

        wall_tile.clear_token("wall")

    def check_if_overdose(self, item):
        pass

    def _get_lateral_range(
        self, y_position: int, side_move: int, mov_range: list[tuple], dungeon_layout
    ) -> None:

        if self.position[1] - side_move >= 0:  # if room in left side
            mov_range.add((y_position, self.position[1] - side_move))  # one step left.

        if self.position[1] + side_move < dungeon_layout.cols:  # if room in right side
            mov_range.add((y_position, self.position[1] + side_move))  # one step right


class Monster(Character, ABC):

    data: list = list()

    # INSTANCE METHODS

    def __init__(self):
        super().__init__()
        self.kind: str = "monster"
        self.blocked_by = ("wall", "player")
        self.cannot_share_tile_with: tuple = ("wall", "monster", "player")
        self.chases: tuple = ("player", None)
        self.ignores: tuple = ("pickable",)  # token_kind or token_species, not both

    @abstractmethod
    def move(self):
        pass

    def attack_players(self):

        players: list = Player.data[:]

        for player in players:
            if utils.are_nearby(self, player) and self.stats.remaining_moves > 0:

                player_tile: tiles.Tile = self.dungeon.get_tile(player.position)
                self.fight_on_tile(player_tile)

    def find_closest_reachable_target(
        self, target_token: tuple[str] = (None, None)
    ) -> tiles.Tile | None:  # pass target_token as (token_kind, token_species)
        """
        Finds closest target based on len(path) and returns the tile where this target is placed
        Returns tile is there is path to tile, None if tile is unreachable"
        """

        tiles_and_paths: list = list()
        start_tile: tiles.Tile = self.dungeon.get_tile(self.position)

        for tile in self.dungeon.children:
            if tile.has_token(target_token):

                if (  # if tile is full and monster wants to land there
                    target_token[0] not in self.cannot_share_tile_with
                    and tile.second_token is not None
                ):
                    continue
                path = self.dungeon.find_shortest_path(
                    start_tile, tile, self.blocked_by
                )
                tiles_and_paths.append((tile, path))

        closest_tile_and_path = None

        for tile_and_path in tiles_and_paths:
            if tile_and_path[1] is not None:  # if path is not None
                if closest_tile_and_path is None or len(closest_tile_and_path[1]) > len(
                    tile_and_path[1]
                ):

                    closest_tile_and_path = tile_and_path

        return None if closest_tile_and_path is None else closest_tile_and_path[0]

    def assess_path_smart(self, target_tile: tiles.Tile) -> list[tuple] | None:

        accesses: list[list] | None = self._find_accesses(target_tile)

        i = 0
        while i < len(accesses):

            # if access is unreachable, remove access
            path_access_end: list[tuple] | None = self.dungeon.find_shortest_path(
                self.token.start,
                self.dungeon.get_tile(accesses[i][-1]),
                self.blocked_by,
            )
            if path_access_end is None:
                accesses.remove(accesses[i])
                continue

            # remove all accesses longer than first access (the shortest)
            elif len(accesses[i]) > len(accesses[0]):
                accesses.remove(accesses[i])
                continue

            # if access end further away from target than monster is, remove access
            else:
                monster_to_target: list[tuple] = self.dungeon.find_shortest_path(
                    self.token.start, target_tile, self.blocked_by
                )
                target_to_access_end: list[tuple] = self.dungeon.find_shortest_path(
                    target_tile, self.dungeon.get_tile(accesses[i][-1]), self.blocked_by
                )

                if len(target_to_access_end) > len(monster_to_target):
                    accesses.remove(accesses[i])
                    continue

            i += 1

        path: list[tuple] | None = None

        for access in accesses:

            end_tile: tiles.Tile = self.dungeon.get_tile(access[-1])
            path_to_access: list[tuple] | None = self.dungeon.find_shortest_path(
                self.token.start, end_tile, self.blocked_by
            )
            if path_to_access is not None:
                if path is None or len(path) > len(path_to_access):
                    path = path_to_access

        if self.chases[0] not in self.cannot_share_tile_with:
            path = self._add_target_position_to_path(path)

        return path

    def assess_path_direct(self, target_tile: tiles.Tile):

        accesses: list[list] | None = self._find_accesses(target_tile, smart=False)

        path: list[tuple] | None = None

        for access in accesses:

            if path:
                break

            end_tile = self.dungeon.get_tile(access[-1])

            possible_path: list[tuple] = self.dungeon.find_shortest_path(
                self.token.start, end_tile, self.blocked_by
            )

            if not possible_path:
                continue

            distance: int = utils.get_distance(self.position, target_tile.position)

            for position in possible_path:

                if distance <= utils.get_distance(position, target_tile.position):

                    break

                elif distance > utils.get_distance(position, target_tile.position):

                    distance = utils.get_distance(position, target_tile.position)

                if possible_path.index(position) == len(possible_path) - 1:

                    path = possible_path

        if self.chases[0] not in self.cannot_share_tile_with:
            path = self._add_target_position_to_path(path)

        return path

    def assess_path_random(self):

        path: list | None = list()

        position: tuple = self.position

        for move in range(self.stats.moves):

            trigger: int = randint(1, 10)

            if trigger <= self.stats.random_motility:

                direction: int = randint(1, 4)  # 1: NORTH, 2: EAST, 3: SOUTH, 4: WEST

                if direction == 1 and self._goes_through(
                    self.dungeon.get_tile((position[0] - 1, position[1]))
                ):

                    position: tuple = (position[0] - 1, position[1])
                    path.append(position)

                elif direction == 2 and self._goes_through(
                    self.dungeon.get_tile((position[0], position[1] + 1))
                ):

                    position: tuple = (position[0], position[1] + 1)
                    path.append(position)

                elif direction == 3 and self._goes_through(
                    self.dungeon.get_tile((position[0] + 1, position[1]))
                ):

                    position: tuple = (position[0] + 1, position[1])
                    path.append(position)

                elif direction == 4 and self._goes_through(
                    self.dungeon.get_tile((position[0], position[1] - 1))
                ):

                    position: tuple = (position[0], position[1] - 1)
                    path.append(position)

        if len(path) > 0:
            path = self._check_free_landing(path)

        return path if len(path) > 0 else None

    def _find_accesses(
        self, target_tile: tiles.Tile, smart: bool = True
    ) -> list[list] | None:
        """
        Returns a list of paths, sorted from shorter to longer,
        from target to all free tiles in the dungeon
        path[-1] is position of free tile in the dungeon, path[0] is position nearby to target_tile
        """

        paths = list()

        # look which tile positions are free in the dungeon among ALL tiles
        scanned: list[tuple] = self.dungeon.scan(
            self.cannot_share_tile_with, exclude=True
        )

        # find paths from target_tile to all free tiles scanned
        for tile_position in scanned:

            scanned_tile: tiles.Tile = self.dungeon.get_tile(tile_position)

            if (
                smart
            ):  # smart creatures avoid tiles where, althogh closer in position, the path to target is longer
                path: list[tuple] = self.dungeon.find_shortest_path(
                    target_tile, scanned_tile, self.blocked_by
                )

            else:
                path: list[tuple] = self.dungeon.find_shortest_path(
                    target_tile, scanned_tile
                )

            if path:

                paths.append(path)

        # sort paths from player to free tiles from shortest to longest

        sorted_paths = sorted(paths, key=len)

        return sorted_paths if len(sorted_paths) > 0 else None

    def _goes_through(self, tile):

        if tile:

            if tile.token and tile.token.kind in self.blocked_by:
                return False
            if tile.second_token and tile.second_token.kind in self.blocked_by:
                return False

            return True

        return False

    def _check_free_landing(self, path: list[tuple]):

        for position in reversed(path):

            if path.index(position) != len(path) - 1:
                break  # at this stage only last position in path is rellevant

            for token_kind in self.cannot_share_tile_with:

                # position != self.position is necessary for random moves
                if (
                    self.dungeon.get_tile(position).has_token((token_kind, None))
                    and position != self.position
                ):

                    path.remove(position)

        return path

    def _add_target_position_to_path(self, path: list[tuple]):

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for direction in directions:

            if path is None:  # monster and target are nearby
                end_tile = self.dungeon.get_tile(
                    (
                        self.position[0] + direction[0],
                        self.position[1] + direction[1],
                    )
                )

            else:
                end_tile = self.dungeon.get_tile(
                    (path[-1][0] + direction[0], path[-1][1] + direction[1])
                )

            if end_tile is not None and end_tile.has_token(self.chases):
                if utils.are_nearby(self, end_tile):
                    path = [end_tile.position]
                else:
                    path.append(end_tile.position)
                break
        return path


class Sawyer(Player):
    """Slow digger (takes half of initial moves each dig)
    Can pick gems
    LOW strength
    LOW health
    HIGH movement"""

    def __init__(self):
        super().__init__()
        self.char: str = "%"
        self.name: str = "Sawyer"
        self.stats = stats.SawyerStats()


class CrusherJane(Player):
    """Can fight with no weapons (MEDIUM strength)
    Stronger if fight with weapons  (HIGH strength)
    Cannot pick gems
    LOW movement
    """

    def __init__(self):
        super().__init__()
        self.char: str = "&"
        self.name: str = "Crusher Jane"
        self.free_actions: tuple = ("fighting",)
        self.ignores: tuple = ("gem",)
        self.stats = stats.CrusherJaneStats()


class Hawkins(Player):
    """Can dig without shovels
    Does not pick shovels
    Can fight with weapons
    Cannot pick gems
    LOW health
    MEDIUM strength
    MEDIUM movement"""

    def __init__(self):
        super().__init__()
        self.char: str = "?"
        self.name: str = "Hawkins"
        self.free_actions: tuple = ("digging",)
        self.ignores: tuple = ("shovel", "gem")
        self.stats = stats.HawkinsStats()


class Kobold(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "K"
        self.name: str = "Kobold"
        self.stats = stats.KoboldStats()

    def move(self):
        return self.assess_path_random()


class CaveHound(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "H"
        self.name: str = "Cave Hound"
        self.stats = stats.CaveHoundStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_direct(target_tile)

        else:
            return self.assess_path_random()


class DepthsWisp(Monster):

    def __init__(self):
        super().__init__()
        self.blocked_by: tuple = ()
        self.cannot_share_tile_with: tuple = ("monster", "player")
        self.ignores: tuple = self.ignores + ("rock",)

        self.char: str = "W"
        self.name: str = "Depths Wisp"
        self.stats = stats.DepthsWispStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_direct()

        else:
            return self.assess_path_random()


class RockElemental(Monster):
    pass

    # moves randomly and slowly but extremely strong if hits


class NightMare(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "N"
        self.name: str = "Nightmare"
        self.stats = stats.NightmareStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_smart(target_tile)

        else:
            return None


class DarkDwarf(Monster):
    pass

    # chases the player. Intermediate strength


class MetalEater(Monster):
    pass

    # chases weapons and shovels and makes disappear. Does not attack player.


class GreedyGnome(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "G"
        self.name: str = "Greedy Gnome"
        self.chases: tuple = ("pickable", "gem")
        self.stats = stats.GreedyGnomeStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if self.dungeon.get_tile(self.position).has_token(self.chases):
            return

        elif target_tile is not None:
            return self.assess_path_smart(target_tile)

        else:
            return self.assess_path_random()
