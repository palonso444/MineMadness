from __future__ import annotations
from random import randint, choice
from abc import ABC, abstractmethod

import game_stats as stats
from character_class import Character


class Monster(Character, ABC):

    data: list = list()

    def __init__(self):
        super().__init__()
        self.kind: str = "monster"
        self.blocked_by: list[str] = ["wall", "player"]
        self.cannot_share_tile_with: list[str] = ["wall", "monster", "player"]
        self.ignores: list[str] = ["pickable"]  # token_kind or token_species, not both

        # exclusive of Monster class
        self.chases: str = "player"

    @abstractmethod
    def move(self):
        pass

    @property
    def has_all_gems(self) -> bool:
        """
        Placeholder, Monsters are not able to collect gems. Needed to avoid crashing when landing on exit Tile
        :return: False
        """
        return False

    def can_dig(self, token_species: str) -> bool:
        """
        Placeholder, monsters are not able to dig so far
        :param token_species: Token.species of the wall
        :return: False
        """
        return False

    def can_fight(self, token_species: str) -> bool:
        """
        Placeholder, monsters are always able to fight
        :param token_species: Token.species of the opponent
        :return: True
        """
        return True

    def can_dodge(self, nearby_spaces: set[tuple[int,int]]) -> bool:
        """
        Determines if the Monster can dodge depending on its dodging_ability and the number of
        nearby spaces
        :param nearby_spaces: tuple containing the coordinates of the nearby spaces
        :return: True if the Monster is able to dodge, False otherwise
        """
        return randint(1, 10) + (4 - len(nearby_spaces)) <= self.stats.dodging_ability

    def move_token_or_behave(self, path) -> None:
        if path is not None:
            self.token.slide(path, self.token.on_move_completed)
        else:
            self.act_on_tile(self.token.get_current_tile())


    def act_on_tile(self, tile: Tile) -> None:
        self.attack_players()
        #self.stats.remaining_moves = 0
        self.get_dungeon().game.update_switch("character_done")


    def generate_dodge_path(self) -> list [tuple[int,int]] | None:
        """
        Returns dodging path if dodging successful
        :return: path or None
        """
        path: list[tuple[int,int]] = list()
        center_position = self.token.position
        for _ in range(self.stats.dodging_moves):
            nearby_spaces: set[tuple[int, int]] = self.token.dungeon.get_nearby_spaces(center_position,
                                                                                       self.cannot_share_tile_with)
            if len(nearby_spaces) > 0 and self.can_dodge(nearby_spaces):
                next_position = choice(list(nearby_spaces))
                path.append(next_position)
                center_position = next_position
        return path if len(path) > 0 else None

    def attack_players(self):
        """
        Manages attack of monsters to surrounding players
        :return:
        """
        surrounding_tiles = [self.token.dungeon.get_tile(position)
                             for position in self.token.dungeon.get_nearby_positions(self.token.position)]

        for tile in surrounding_tiles:
            if self.stats.remaining_moves == 0:
                break
            if tile.has_token("player"):
                self.fight_on_tile(tile)

    def fight_on_tile(self, opponent_tile: Tile) -> None:
        opponent = opponent_tile.tokens["player"].character
        opponent = self.fight_opponent(opponent)
        opponent.token.bar_length = (
                opponent.stats.health / opponent.stats.natural_health
        )

        if opponent.stats.health <= 0:
            opponent.kill_character(opponent_tile)

    def find_closest_reachable_target(self, target_token: str) -> Tile | None:  # pass target_token as (token_kind, token_species)
        """
        Finds closest target based on len(path) and returns the tile where this target is placed
        Returns tile if there is path to tile, None if tile is unreachable"
        """

        tiles_and_paths: list = list()
        start_tile: Tile = self.token.get_current_tile()

        for tile in self.token.dungeon.children:
            if tile.has_token(target_token):

                if target_token == "player" and tile.tokens["player"].character.is_hidden:
                    continue

                path = self.token.dungeon.find_shortest_path(
                    start_tile.position, tile.position, self.blocked_by
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
        if (self.token.dungeon.are_nearby(self.token.position, target_tile.position)
                and self.chases in self.cannot_share_tile_with):
            return None

        accesses: list[list] | None = self._find_accesses(target_tile, smart=True)

        i = 0
        while i < len(accesses):

            # if access is unreachable or too far away, remove access
            path_access_end: list[tuple] | None = self.token.dungeon.find_shortest_path(
                self.token.position,
                self.token.dungeon.get_tile(accesses[i][-1]).position,
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
                monster_to_target: list[tuple] = self.token.dungeon.find_shortest_path(
                    self.token.position, target_tile.position, self.blocked_by
                )
                target_to_access_end: list[tuple] = self.token.dungeon.find_shortest_path(
                    target_tile.position, self.token.dungeon.get_tile(accesses[i][-1]).position, self.blocked_by
                )

                if len(target_to_access_end) > len(monster_to_target):
                    accesses.remove(accesses[i])
                    continue

            i += 1

        path: list[tuple] | None = None

        for access in accesses:

            end_tile: Tile = self.token.dungeon.get_tile(access[-1])
            path_to_access: list[tuple] | None = self.token.dungeon.find_shortest_path(
                self.token.position, end_tile.position, self.blocked_by
            )
            if path_to_access is not None:
                if path is None or len(path) > len(path_to_access):
                    path = path_to_access

        # this allows monster to end on pickables
        if self.chases not in self.cannot_share_tile_with:
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

            access_tile = self.token.dungeon.get_tile(access[-1])
            possible_path: list[tuple] = self.token.dungeon.find_shortest_path(
                self.get_position(), access_tile.position, self.blocked_by
            )

            # if access unreachable or too far away, check another one
            if possible_path is None or len(possible_path) > self.stats.remaining_moves:
                continue

            # get distance to player
            distance_to_target: int = self.token.dungeon.get_distance(
                self.token.position, target_tile.position
            )

            # for each position in path
            for idx, position in enumerate(possible_path):

                # if going to that position means going further away from player, path not valid
                if distance_to_target <= self.token.dungeon.get_distance(
                    position, target_tile.position
                ):
                    break

                # if going to that position means getting closer to player, path OK so far
                if distance_to_target > self.token.dungeon.get_distance(
                    position, target_tile.position
                ):
                    # update distance to target from this new position
                    distance_to_target = self.token.dungeon.get_distance(
                        position, target_tile.position
                    )

                # if this was the last position of path, path approved
                if idx == len(possible_path) - 1:
                    path = possible_path

        # this makes monster able to end on pickables
        if self.chases not in self.cannot_share_tile_with:
            path = self._add_target_position_to_path(path)

        return path

    def assess_path_random(self):
        """
        Returns a random path with a maximmum length equal to the remaining moves of the monster.
        """

        path: list | None = list()
        position: tuple = self.token.position

        for _ in range(self.stats.remaining_moves):

            trigger: int = randint(1, 10)

            if trigger <= self.stats.random_motility:
                direction: int = randint(1, 4)  # 1: NORTH, 2: EAST, 3: SOUTH, 4: WEST

                if direction == 1 and self._goes_through(
                    self.token.dungeon.get_tile((position[0] - 1, position[1]))
                ):

                    position: tuple = (position[0] - 1, position[1])
                    path.append(position)

                elif direction == 2 and self._goes_through(
                    self.token.dungeon.get_tile((position[0], position[1] + 1))
                ):

                    position: tuple = (position[0], position[1] + 1)
                    path.append(position)

                elif direction == 3 and self._goes_through(
                    self.token.dungeon.get_tile((position[0] + 1, position[1]))
                ):

                    position: tuple = (position[0] + 1, position[1])
                    path.append(position)

                elif direction == 4 and self._goes_through(
                    self.token.dungeon.get_tile((position[0], position[1] - 1))
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
        scanned: list[tuple] = self.token.dungeon.scan_tiles(
            self.cannot_share_tile_with, exclude=True
        )

        # find paths from target_tile to all free tiles scanned
        for tile_position in scanned:

            scanned_tile: tiles.Tile = self.token.dungeon.get_tile(tile_position)

            if (
                smart
            ):  # smart creatures avoid tiles where, althogh closer in position, the path to target is longer
                path: list[tuple] = self.token.dungeon.find_shortest_path(
                    target_tile.position, scanned_tile.position, self.blocked_by
                )

            else:
                path: list[tuple] = self.token.dungeon.find_shortest_path(
                    target_tile.position, scanned_tile.position
                )

            if path:

                paths.append(path)

        # sort paths from player to free tiles from shortest to longest

        sorted_paths = sorted(paths, key=len)

        return sorted_paths if len(sorted_paths) > 0 else None

    def _goes_through(self, tile):

        if tile:
            return all(tile.tokens[token_kind] is None for token_kind in self.blocked_by)

    def _check_free_landing(self, path: list[tuple]):

        idx_to_remove = set()
        last_idx = len(path) - 1

        for i, position in enumerate(reversed(path)):

            if (
                any(
                    self.token.dungeon.get_tile(position).has_token(token_kind)
                    for token_kind in self.cannot_share_tile_with
                )
                # position != self.position is necessary for random moves
                and position != self.token.position
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
                end_tile = self.token.dungeon.get_tile(
                    (
                        self.token.position[0] + direction[0],
                        self.token.position[1] + direction[1],
                    )
                )

            else:
                end_tile = self.token.dungeon.get_tile(
                    (path[-1][0] + direction[0], path[-1][1] + direction[1])
                )

            if end_tile is not None and end_tile.has_token(self.chases) and not any(end_tile.has_token(token_kind) for
                                                                                    token_kind in self.cannot_share_tile_with):
                if self.token.dungeon.are_nearby(self.token.position, end_tile.position):
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
        self.species: str = "kobold"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.KoboldStats()

    def move(self):
        super().move_token_or_behave(self.assess_path_random())


class BlindLizard(Monster):
    """
    MEDIUM movement
    MEDIUM strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "L"
        self.name: str = "Blind Lizard"
        self.species: str = "lizard"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.BlindLizardStats()

    def move(self):
        super().move_token_or_behave(self.assess_path_random())


class BlackDeath(Monster):
    """
    VERY HIGH  movement
    VERY HIGH strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "B"
        self.name: str = "Black Death"
        self.species: str = "blackdeath"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.BlackDeathStats()

    def move(self):
        super().move_token_or_behave(self.assess_path_random())


# DIRECT MOVEMENT MONSTERS


class CaveHound(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "H"
        self.name: str = "Cave Hound"
        self.species: str = "hound"
        self.step_transition: str = "in_quart"  # gallop
        self.step_duration: float = 0.3
        self.stats = stats.CaveHoundStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_direct(target_tile))
        else:
            super().move_token_or_behave(self.assess_path_random())


class Growl(Monster):
    """
    MEDIUM movement
    HIGH strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "G"
        self.name: str = "Growl"
        self.species: str = "growl"
        self.step_transition: str = "in_out_elastic"  # stomping
        self.step_duration: float = 0.7
        self.stats = stats.GrowlStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_direct(target_tile))
        else:
            super().move_token_or_behave(self.assess_path_random())


class RockGolem(Monster):
    """
    LOW movement
    VERY HIGH strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "R"
        self.name: str = "Rock Golem"
        self.species: str = "golem"
        self.step_transition: str = "in_out_elastic"  # stomping
        self.step_duration: float = 0.7
        self.stats = stats.RockGolemStats()

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_direct(target_tile))
        else:
            super().move_token_or_behave(None)


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
        self.species: str = "gnome"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.DarkGnomeStats()

    def move(self):

        target_tile: Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_smart(target_tile))
        else:
            super().move_token_or_behave(self.assess_path_random())


class NightMare(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "N"
        self.name: str = "Nightmare"
        self.species: str = "nightmare"
        self.step_transition: str = "in_quart"  # gallop
        self.step_duration: float = 0.3
        self.stats = stats.NightmareStats()

    def move(self):

        target_tile: Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_smart(target_tile))
        else:
            return super().move_token_or_behave(self.assess_path_random())


class LindWorm(Monster):

    def __init__(self):
        super().__init__()
        self.char: str = "Y"
        self.name: str = "Lindworm"
        self.species: str = "lindworm"
        self.step_transition: str = "in_out_elastic"  # stomping
        self.step_duration: float = 0.7
        self.stats = stats.LindWormStats()

    def move(self):

        target_tile: Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_smart(target_tile))
        else:
            super().move_token_or_behave(None)


# GHOSTS


class WanderingShadow(Monster):
    """
    RANDOM HIGH movement
    MEDIUM strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "S"
        self.name: str = "Wandering Shadow"
        self.species: str = "shadow"
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.3
        self.stats = stats.WanderingShadowStats()

        self.blocked_by: list = []
        self.cannot_share_tile_with: list[str] = ["monster", "player"]
        self.ignores: list[str] = self.ignores + ["rock"]



    def move(self):
        super().move_token_or_behave(self.assess_path_random())


class DepthsWisp(Monster):
    """
    DIRECT MEDIUM movement
    LOW strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "W"
        self.name: str = "Depths Wisp"
        self.species: str = "wisp"
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.3
        self.stats = stats.DepthsWispStats()

        self.blocked_by: list = []
        self.cannot_share_tile_with: list[str] = ["monster", "player"]
        self.ignores: list[str] = self.ignores + ["rock"]



    def move(self):

        target_tile: Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_direct(target_tile))
        else:
            super().move_token_or_behave(None)


class MountainDjinn(Monster):
    """
    DIRECT MEDIUM movement
    HIGH strength
    """

    def __init__(self):
        super().__init__()
        self.char: str = "D"
        self.name: str = "Mountain Djinn"
        self.species: str = "djinn"
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.3
        self.stats = stats.MountainDjinnStats()

        self.blocked_by: list = []
        self.cannot_share_tile_with: list[str] = ["monster", "player"]
        self.ignores: list[str] = self.ignores + ["rock"]



    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_direct(target_tile))
        else:
            super().move_token_or_behave(None)


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
        self.species: str = "pixie"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.PixieStats()

        self.chases: str = "pickable"


    def act_on_tile(self, tile: Tile) -> None:
        """
        Consumes pickables before calling the parent method
        :param tile: Tile on which to act
        :return: None
        """
        if tile.has_token("pickable"):
            tile.get_token("pickable").delete_token(tile)
        super().act_on_tile(tile)

    def move(self):

        target_tile: tiles.Tile | None = self.find_closest_reachable_target(self.chases)

        if target_tile is not None:
            super().move_token_or_behave(self.assess_path_smart(target_tile))
        else:
            super().move_token_or_behave(self.assess_path_random())