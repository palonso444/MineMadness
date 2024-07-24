from random import randint, choice
from abc import ABC, abstractmethod
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher
from kivy.graphics import Color

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

    @classmethod
    def all_out_of_game(cls) -> bool:
        """
        Checks if all instances of the class (players or monsters) dead or out of game
        """

        if len(cls.data) == 0:
            return True
        return False

    # INSTANCE METHODS

    def __init__(self):

        self.name: str | None = None
        self.inventory: dict | None = None
        self.id: int | None = None
        self.position: tuple | None = None

        # monsters need ability_active for the functioning of the ability_button
        self.ability_active: bool = False

        self.token = None
        self.dungeon = None

    def using_dynamite(self):  # needed for everybody for Token.on_slide_completed()
        return False

    def is_hidden(self):  # needed for everybody for self.fight_on_tile()
        return False

    def update_position(self, position: tuple[int]) -> None:
        self.__class__.data[self.id].position = position

    def fight_on_tile(self, opponent_tile: tiles.Tile) -> None:

        opponent = opponent_tile.get_character()
        game = self.dungeon.game
        self.stats.remaining_moves -= 1
        damage = randint(self.stats.strength[0], self.stats.strength[1])

        if (
            isinstance(self, CrusherJane) or isinstance(self, Sawyer)
        ) and self.ability_active:
            damage += self.stats.advantage_strength_incr

        if self.is_hidden():
            self.unhide()
            if isinstance(self, Sawyer):
                self.ability_active = False
                game.update_switch("ability_button")

        if "fighting" not in self.free_actions or (
            isinstance(self, CrusherJane) and self.ability_active
        ):
            self.stats.weapons -= 1
            game.update_switch("weapons")
            if isinstance(self, CrusherJane) and self.stats.weapons == 0:
                self.ability_active = False
                game.update_switch("ability_button")

        if isinstance(opponent, Player):
            damage = opponent._apply_thoughness(damage)

        opponent.stats.health = opponent.stats.health - damage
        if opponent.token.percentage_natural_health is not None:
            opponent.token.percentage_natural_health = (
                opponent.stats.health / opponent.stats.natural_health
            )

        if opponent.stats.health <= 0:
            opponent.kill_character(opponent_tile)
            if isinstance(opponent, Monster):
                self.experience += opponent.stats.experiece_when_killed
                game.ids.experience_bar.value = self.experience

        self.dungeon.show_damage_token(
            opponent.token.shape.pos, opponent.token.shape.size
        )

    def has_moved(self) -> bool:

        if self.stats.remaining_moves == self.stats.moves:
            return False
        return True

    def kill_character(self, tile):

        character = self.__class__.data.pop(self.id)
        self.__class__.rearrange_ids()
        tile.clear_token(self.token.kind)
        if isinstance(character, Player):
            Player.dead_data.append(character)

    # MOVEMENT METHODS TO IMPLEMENT

    def glide(self):
        raise NotImplementedError()

    def walk(self):
        raise NotImplementedError()

    def stomp(self):
        raise NotImplementedError()


class Player(Character, ABC, EventDispatcher):

    experience = NumericProperty(0)
    player_level = NumericProperty(1)

    # this is the starting order as defined by Player.set_starting_player_order()
    player_chars: tuple = ("%", "?", "&")  # % sawyer, ? hawkins, & crusher jane
    data: list = list()
    dead_data: list = list()
    exited: set = set()
    gems: int = 0

    @classmethod
    def set_starting_player_order(cls) -> None:

        sawyer = next(player for player in cls.data if isinstance(player, Sawyer))
        hawkins = next(player for player in cls.data if isinstance(player, Hawkins))
        crusherjane = next(
            player for player in cls.data if isinstance(player, CrusherJane)
        )

        cls.data = [sawyer, hawkins, crusherjane]
        cls.rearrange_ids()

    @classmethod
    def transfer_player(cls, name: str) -> Character:
        """
        Heals and disables the ability of exited players and transfers them to the next level.
        """

        for player in cls.exited:
            if player.name == name:
                player.heal(player.stats.recovery_end_of_level)
                player.ability_active = False
                return player

    @abstractmethod
    def on_player_level(self, instance, value):
        pass

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
            "talisman": 10,
        }
        self.special_items: dict[str:int] | None = None
        self.effects: dict[str:list] = {"moves": [], "thoughness": [], "strength": []}
        self.state: str | None = None
        self.level_track: dict[int:dict] = {}
        self.bind(experience=self.on_experience)
        self.bind(player_level=self.on_player_level)

    # default using_dynamite() defined in Character class
    # default is_hidden() defined in Character class

    def on_experience(self, instance, value):

        if value >= self.stats.exp_to_next_level:
            self.player_level += 1
            self.stats.exp_to_next_level = (
                self.player_level * self.stats.base_exp_to_level_up
            )
            self.experience = 0
            # experience bar updated by Cragpeongame.update_interface()
            print("UPDATEEE")

            print("TO NEXT LEVEL")
            print(self.stats.exp_to_next_level)

    def remove_effects(self, turn: int) -> None:
        """
        Removes all effects for which the effect is over
        """

        attribute_names = list()

        # attributes are: "moves", "thoughness", "strength"
        for attribute, effects in self.effects.items():

            i = 0
            while i < len(effects):

                if effects[i]["end_turn"] <= turn:
                    player_stat = getattr(self.stats, attribute)

                    if isinstance(player_stat, int):
                        new_value = player_stat - effects[i]["size"]
                    elif isinstance(player_stat, tuple):
                        new_value = (
                            player_stat[0],
                            player_stat[1] - effects[i]["size"],
                        )

                    effects.remove(effects[i])
                    attribute_names.append(attribute)
                    setattr(self.stats, attribute, new_value)
                    continue
                i += 1

        if len(attribute_names) > 0:
            item_names = utils.match_attribute_to_item(attribute_names)
            self.dungeon.fading_token_character = self
            self.dungeon.fading_tokens_effect_fades = True
            self.dungeon.fading_tokens_items_queue = item_names

    def get_range(self, dungeon_layout, range_kind: str):
        # TODO: DO NOT ACTIVATE IF WALLS ARE PRESENT
        # TODO: better as method of Player Class

        mov_range: set[tuple] = set()
        if range_kind == "movement":
            remaining_moves = self.stats.remaining_moves
        elif range_kind == "shooting":
            remaining_moves = self.stats.shooting_range

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

            elif (
                self.special_items is not None
                and tile.token.species in self.special_items.keys()
            ):
                self.special_items[tile.token.species] += 1
                game.update_switch("ability_button")

            elif tile.token.species in self.inventory.keys():
                self.inventory[tile.token.species] += 1
                game.inv_object = tile.token.species

            else:
                character_attribute = getattr(self.stats, tile.token.species + "s")
                character_attribute += 1
                setattr(self.stats, tile.token.species + "s", character_attribute)
                game.update_switch(tile.token.species + "s")
                game.update_switch("ability_button")  # for Crusher Jane

            tile.clear_token(tile.token.kind)

    def dig(self, wall_tile: tiles.Tile) -> None:

        game = self.dungeon.game

        if self.stats.shovels > 0:
            if "digging" not in self.free_actions or wall_tile.has_token(
                ("wall", "granite")
            ):
                self.stats.shovels -= 1
                game.update_switch("shovels")
        self.stats.remaining_moves -= self.stats.digging_moves

        self.dungeon.show_digging_token(
            wall_tile.token.shape.pos, wall_tile.token.shape.size
        )

        wall_tile.clear_token("wall")

        # if digging a wall recently created by dynamite
        if wall_tile.dodging_finished:
            wall_tile.dodging_finished = False

    def heal(self, extra_points: int):
        self.stats.health = (
            self.stats.health + extra_points
            if self.stats.health + extra_points <= self.stats.natural_health
            else self.stats.natural_health
        )

    def resurrect(self):

        self.player_level = self.player_level - 3 if self.player_level > 3 else 1

        for key, value in self.level_track[self.player_level].items():
            self.stats.__setattr__(key, value)

        # equals attributes to natural_attributes
        self.stats.__post_init__()

        self.experience = 0
        self.stats.exp_to_next_level = (
            self.player_level * self.stats.base_exp_to_level_up
        )

        for value in self.inventory.values():
            value = 0
        if self.special_items is not None:
            for value in self.special_items.values():
                value = 0

        location: tiles.Tile = self.dungeon.get_random_tile(free=True)

        self.dungeon.place_item(location, self.token.kind, self.token.species, self)

        print(self.player_level)
        print(self.stats)

    def _apply_thoughness(self, damage):

        i = 0
        while i < len(self.effects["thoughness"]):
            self.effects["thoughness"][i]["size"] -= damage

            if self.effects["thoughness"][i]["size"] <= 0:
                damage = abs(self.effects["thoughness"][i]["size"])
                self.effects["thoughness"].remove(self.effects["thoughness"][i])
                continue

            elif self.effects["thoughness"][i]["size"] > 0:
                damage = 0
                break

        return damage

    def check_if_overdose(self, item):
        pass

    def _update_level_track(self, level: int) -> None:

        self.level_track[level] = {
            "health": self.stats.natural_health,
            "moves": self.stats.natural_moves,
            "strength": self.stats.natural_strength,
        }

    def _get_lateral_range(
        self, y_position: int, side_move: int, mov_range: list[tuple], dungeon_layout
    ) -> None:

        if self.position[1] - side_move >= 0:  # if room in left side
            mov_range.add((y_position, self.position[1] - side_move))  # one step left.

        if self.position[1] + side_move < dungeon_layout.cols:  # if room in right side
            mov_range.add((y_position, self.position[1] + side_move))  # one step right

    def _level_up_health(self, increase: int) -> None:

        self.stats.natural_health += increase
        self.stats.health += increase

    def _level_up_moves(self, increase: int) -> None:

        self.stats.natural_moves += increase
        self.stats.moves += increase
        self.stats.remaining_moves += increase
        self.dungeon.game.dynamic_movement_range()

    def _level_up_strength(self, increase: tuple[int]) -> None:

        self.stats.natural_strength = (
            self.stats.natural_strength[0] + increase[0],
            self.stats.natural_strength[1] + increase[1],
        )
        self.stats.strength = (
            self.stats.strength[0] + increase[0],
            self.stats.strength[1] + increase[1],
        )


class Monster(Character, ABC):

    data: list = list()

    # INSTANCE METHODS

    def __init__(self):
        super().__init__()
        self.kind: str = "monster"
        self.blocked_by = ("wall", "player")
        self.cannot_share_tile_with: tuple = ("wall", "monster", "player")
        self.free_actions: tuple = ("fighting",)
        self.chases: tuple = ("player", None)
        self.ignores: tuple = ("pickable",)  # token_kind or token_species, not both

    @abstractmethod
    def move(self):
        pass

    def try_to_dodge(self):

        random_num = randint(1, 10)
        surrounding_spaces = self.dungeon.get_surrounding_spaces(
            self.position, self.cannot_share_tile_with
        )
        trigger = random_num + (4 - len(surrounding_spaces))

        if trigger <= self.stats.dodging_ability and len(surrounding_spaces) > 0:
            end_position = choice(list(surrounding_spaces))
            self._dodge(end_position)
        else:
            self.dungeon.get_tile(self.position).dodging_finished = True

    def attack_players(self):

        players: list = Player.data[:]

        for player in players:
            if utils.are_nearby(self, player) and self.stats.remaining_moves > 0:

                if player.is_hidden():
                    player.unhide()
                    if isinstance(player, Sawyer):
                        player.ability_active = False
                        # ability_button updated automatically when players turn

                player_tile: tiles.Tile = self.dungeon.get_tile(player.position)
                self.fight_on_tile(player_tile)

    def find_closest_reachable_target(
        self, target_token: tuple[str] = (None, None)
    ) -> tiles.Tile | None:  # pass target_token as (token_kind, token_species)
        """
        Finds closest target based on len(path) and returns the tile where this target is placed
        Returns tile if there is path to tile, None if tile is unreachable"
        """

        tiles_and_paths: list = list()
        start_tile: tiles.Tile = self.dungeon.get_tile(self.position)

        for tile in self.dungeon.children:
            if tile.has_token(target_token):

                if (
                    target_token[0] == "player"
                    and isinstance(tile.get_character(), Sawyer)
                    and tile.get_character().ability_active
                ):
                    continue

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
        """
        Returns the path to the closest tile and with access to the target within the range of
        remaining moves of the monster. Returns None if there is no access to the target or all accesses
        are out of range of remaining moves
        """

        # if target is nearby and cannot share tile with it, don't move
        if utils.are_nearby(self, target_tile):
            return None

        accesses: list[list] | None = self._find_accesses(target_tile, smart=True)

        i = 0
        while i < len(accesses):

            # if access is unreachable or too far away, remove access
            path_access_end: list[tuple] | None = self.dungeon.find_shortest_path(
                self.token.start,
                self.dungeon.get_tile(accesses[i][-1]),
                self.blocked_by,
            )
            if (
                path_access_end is None
                or len(path_access_end) > self.stats.remaining_moves
            ):
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

        # this allows monster to end on pickables
        if self.chases[0] not in self.cannot_share_tile_with:
            path = self._add_target_position_to_path(path)

        return path

    def assess_path_direct(self, target_tile: tiles.Tile) -> list[tuple] | None:
        """
        Returns the path to the closest tile and with access to the target within the range of
        remaining moves of the monster. Returns None if there is no access to the target or all accesses
        are out of range of remaining moves.
        Path returned brings closer the monster to the player with every move.
        """

        accesses: list[list] | None = self._find_accesses(target_tile, smart=False)
        path: list[tuple] | None = None

        for access in accesses:

            if path:
                break

            access_tile = self.dungeon.get_tile(access[-1])
            possible_path: list[tuple] = self.dungeon.find_shortest_path(
                self.token.start, access_tile, self.blocked_by
            )

            # if access unreachable or too far away, check another one
            if possible_path is None or len(possible_path) > self.stats.remaining_moves:
                continue

            # get distance to player
            distance_to_target: int = utils.get_distance(
                self.position, target_tile.position
            )

            # for each position in path
            for idx, position in enumerate(possible_path):

                # if going to that position means going further away from player, path not valid
                if distance_to_target <= utils.get_distance(
                    position, target_tile.position
                ):
                    break

                # if going to that position means getting closer to player, path OK so far
                if distance_to_target > utils.get_distance(
                    position, target_tile.position
                ):
                    # update distance to target from this new position
                    distance_to_target = utils.get_distance(
                        position, target_tile.position
                    )

                # if this was the last position of path, path approved
                if idx == len(possible_path) - 1:
                    path = possible_path

        # this makes monster able to end on pickables
        if self.chases[0] not in self.cannot_share_tile_with:
            path = self._add_target_position_to_path(path)

        return path

    def assess_path_random(self):
        """
        Returns a random path with a maximmum length equal to the remaining moves of the monster.
        """

        path: list | None = list()
        position: tuple = self.position

        for _ in range(self.stats.remaining_moves):

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

    def _dodge(self, end_position: tuple[int]):

        start_tile = self.dungeon.get_tile(self.position)
        end_tile = self.dungeon.get_tile(end_position)
        self.token.start = start_tile
        self.token.goal = end_tile
        self.token.path = [end_position]
        self.token.slide(self.token.path)

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

        idx_to_remove = set()
        last_idx = len(path) - 1

        for i, position in enumerate(reversed(path)):

            if (
                any(
                    self.dungeon.get_tile(position).has_token((token_kind, None))
                    for token_kind in self.cannot_share_tile_with
                )
                # position != self.position is necessary for random moves
                and position != self.position
            ):

                idx = last_idx - i
                idx_to_remove.add(idx)

            else:
                break

        path = [
            position for idx, position in enumerate(path) if idx not in idx_to_remove
        ]

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
        self.special_items: dict[str:int] | None = {"powder": 5}
        self.ignores = ("dynamite",)

        self.stats = stats.SawyerStats()
        self._update_level_track(self.player_level)

    def on_player_level(self, instance, value):
        """Sawyer increases 1 movement per level
        1 advantatge_strength_increase per level
        1 health point every 2 levels
        1 max damage every 2 levels
        1 recovery_end_of_level every 3 levels"""

        self._level_up_moves(1)
        self.stats.advantage_strength_incr += 1

        if not utils.check_if_multiple(value, 2):
            self._level_up_health(1)
            self._level_up_strength((0, 1))

        if not utils.check_if_multiple(value, 3):
            self.stats.recovery_end_of_level += 1

        self._update_level_track(value)

        print(self.level_track)
        print(self.stats)

    def hide(self):
        self.token.color.a = 0.6  # changes transparency
        self.ignores += ("pickable",)

    def unhide(self):
        self.token.color.a = 1  # changes transparency
        self.ignores = utils.tuple_remove(self.ignores, "pickable")

    def is_hidden(self):
        if self.ability_active:
            return True
        return False


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
        self.ignores: tuple = ("gem", "powder", "dynamite")

        self.stats = stats.CrusherJaneStats()
        self._update_level_track(self.player_level)

    def on_player_level(self, instance, value):
        """Crusher Jane increases 1 movement every 2 levels
        1 health point every level
        1 recovery_end_of_level every level
        1 advantatge_strength_increase every 2 levels
        1 max damage every level and 2 min damage every 2 levels"""

        print("CRUSHER JANE LEVEL UP!")
        print(value)

        self._level_up_health(1)
        self._level_up_strength((0, 1))
        self.stats.recovery_end_of_level += 1

        if not utils.check_if_multiple(value, 2):
            self._level_up_moves(1)
            self._level_up_strength((2, 0))
            self.stats.advantage_strength_incr += 1

        self._update_level_track(value)

        print(self.level_track)

        print(self.stats)


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
        self.ignores: tuple = ("gem", "powder")
        self.special_items: dict[str:int] | None = {"dynamite": 100}

        self.stats = stats.HawkinsStats()
        self._update_level_track(self.player_level)

    def on_player_level(self, instance, value):
        """Hawkins increases 1 movement every 2 levels
        1 health point every 2 levels
        1 recovery_end_of_level every 2 levels
        1 max damage every level and 1 min damage every 4 levels"""

        print("HAWKINS LEVEL UP!")
        print(value)

        self._level_up_strength((0, 1))

        if not utils.check_if_multiple(value, 2):
            self._level_up_moves(1)
            self._level_up_health(1)
            self.stats.recovery_end_of_level += 1

        if utils.check_if_multiple(value, 4):
            self._level_up_strength((1, 0))

        self._update_level_track(value)

        print(self.level_track)
        print(self.stats)

    def using_dynamite(self):
        if self.ability_active:
            return True
        return False


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
