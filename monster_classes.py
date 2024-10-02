from __future__ import annotations
from random import randint, choice
from abc import ABC, abstractmethod

import game_stats as stats
from character_classes import Character


class Monster(Character, ABC):

    data: list = list()

    # INSTANCE METHODS

    def __init__(self):
        super().__init__()
        self.kind: str = "monster"
        self.blocked_by = ("wall", "player")
        self.cannot_share_tile_with: tuple = ("wall", "monster", "player")
        self.free_actions: tuple = ("fighting",)  # no need of weapons to fight
        self.chases: tuple = ("player", None)
        self.ignores: tuple = ("pickable",)  # token_kind or token_species, not both

    @abstractmethod
    def move(self):
        pass

    def enhance_damage(self, damage: int) -> int:
        """
        Placeholder needed for fight_on_tile()
        """
        return damage

    def unhide(self) -> None:
        """
        Placeholder needed for fight_on_tile()
        """
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
        """
        Manages attack of monsters to surrounding players
        :return:
        """
        surrounding_tiles = [self.dungeon.get_tile(position) for position in self.dungeon.get_nearby_positions(self.position)]

        for tile in surrounding_tiles:
            if self.stats.remaining_moves == 0:
                break
            character = tile.get_character()
            if character is not None and character.kind == "player":
                self.fight_on_tile(tile)

    def find_closest_reachable_target(
        self, target_token: tuple[str] = (None, None)
    ) -> Tile | None:  # pass target_token as (token_kind, token_species)
        """
        Finds closest target based on len(path) and returns the tile where this target is placed
        Returns tile if there is path to tile, None if tile is unreachable"
        """

        tiles_and_paths: list = list()
        start_tile: Tile = self.dungeon.get_tile(self.position)

        for tile in self.dungeon.children:
            if tile.has_token(target_token):

                # if character is hidden.
                if target_token[0] == "player" and tile.get_character().is_hidden:
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

    def assess_path_smart(self, target_tile: Tile) -> list[tuple] | None:
        """
        Returns the path to the closest tile and with access to the target within the range of
        remaining moves of the monster. Returns None if there is no access to the target or all accesses
        are out of range of remaining moves
        """

        # if target is nearby and cannot share tile with it, don't move
        if self.dungeon.are_nearby(self, target_tile):
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

            end_tile: Tile = self.dungeon.get_tile(access[-1])
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

    def assess_path_direct(self, target_tile: Tile) -> list[tuple] | None:
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
            distance_to_target: int = self.dungeon.get_distance(
                self.position, target_tile.position
            )

            # for each position in path
            for idx, position in enumerate(possible_path):

                # if going to that position means going further away from player, path not valid
                if distance_to_target <= self.dungeon.get_distance(
                    position, target_tile.position
                ):
                    break

                # if going to that position means getting closer to player, path OK so far
                if distance_to_target > self.dungeon.get_distance(
                    position, target_tile.position
                ):
                    # update distance to target from this new position
                    distance_to_target = self.dungeon.get_distance(
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
                if self.dungeon.are_nearby(self, end_tile):
                    path = [end_tile.position]
                else:
                    path.append(end_tile.position)
                break
        return path


# RANDOM MOVEMENT MONSTERS


class Kobold(Monster):
    """
    HIGH movement
    LOW strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "K"
        self.name: str = "Kobold"
        self.stats = stats.KoboldStats()

    def move(self):
        return self.assess_path_random()


class BlindLizard(Monster):
    """
    MEDIUM movement
    MEDIUM strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "L"
        self.name: str = "Blind Lizard"
        self.stats = stats.BlindLizardStats()

    def move(self):
        return self.assess_path_random()


class BlackDeath(Monster):
    """
    VERY HIGH  movement
    VERY HIGH strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "B"
        self.name: str = "Black Death"
        self.stats = stats.BlackDeathStats()

    def move(self):
        return self.assess_path_random()


# DIRECT MOVEMENT MONSTERS


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


class Growl(Monster):
    """
    MEDIUM movement
    HIGH strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "G"
        self.name: str = "Growl"
        self.stats = stats.GrowlStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_direct(target_tile)

        else:
            return self.assess_path_random()


class RockGolem(Monster):
    """
    LOW movement
    VERY HIGH strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "R"
        self.name: str = "Rock Golem"
        self.stats = stats.RockGolemStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_direct(target_tile)

        else:
            return None


# SMART MOVEMENT MONSTERS


class DarkGnome(Monster):
    """
    LOW strength
    MEDIUM movement
    """

    def __init__(self):
        super().__init__()
        self.char: str = "O"
        self.name: str = "Dark Gnome"
        self.stats = stats.DarkGnomeStats()

    def move(self):

        target_tile: Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_smart(target_tile)

        else:
            return self.assess_path_random()


class NightMare(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "N"
        self.name: str = "Nightmare"
        self.stats = stats.NightmareStats()

    def move(self):

        target_tile: Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_smart(target_tile)

        else:
            return self.assess_path_random()


class LindWorm(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "Y"
        self.name: str = "Lindworm"
        self.stats = stats.LindWormStats()

    def move(self):

        target_tile: Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_smart(target_tile)

        else:
            return None


# GHOSTS


class WanderingShadow(Monster):
    """
    RANDOM HIGH movement
    MEDIUM strength
    """

    def __init__(self):
        super().__init__()
        self.blocked_by: tuple = ()
        self.cannot_share_tile_with: tuple = ("monster", "player")
        self.ignores: tuple = self.ignores + ("rock",)

        self.char: str = "S"
        self.name: str = "Wandering Shadow"
        self.stats = stats.WanderingShadowStats()

    def move(self):

        return self.assess_path_random()


class DepthsWisp(Monster):
    """
    DIRECT MEDIUM movement
    LOW strength
    """

    def __init__(self):
        super().__init__()
        self.blocked_by: tuple = ()
        self.cannot_share_tile_with: tuple = ("monster", "player")
        self.ignores: tuple = self.ignores + ("rock",)

        self.char: str = "W"
        self.name: str = "Depths Wisp"
        self.stats = stats.DepthsWispStats()

    def move(self):

        target_tile: Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_direct(target_tile)

        else:
            return None


class MountainDjinn(Monster):
    """
    DIRECT MEDIUM movement
    HIGH strength
    """

    def __init__(self):
        super().__init__()
        self.blocked_by: tuple = ()
        self.cannot_share_tile_with: tuple = ("monster", "player")
        self.ignores: tuple = self.ignores + ("rock",)

        self.char: str = "D"
        self.name: str = "Mountain Djinn"
        self.stats = stats.MountainDjinnStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            return self.assess_path_direct(target_tile)

        else:
            return None


# SPECIAL MONSTERS


class Pixie(Monster):
    """
    HIGH movement
    LOW health
    DOES NOT attack player
    Chases pickables and makes them disappear
    """

    def __init__(self):
        super().__init__()
        self.char: str = "P"
        self.name: str = "Pixie"
        self.chases: tuple = ("pickable", None)
        self.ignores: tuple = self.ignores + ("gem",)
        self.stats = stats.PixieStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if self.dungeon.get_tile(self.position).has_token(self.chases):
            self.dungeon.get_tile(self.position).clear_token("pickable")

        elif target_tile is not None:
            return self.assess_path_smart(target_tile)

        else:
            return self.assess_path_random()