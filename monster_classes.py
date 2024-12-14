from __future__ import annotations
from random import randint, choice
from abc import ABC, abstractmethod

import game_stats as stats
from character_class import Character


class Monster(Character, ABC):

    data: list[Character] = list()

    def __init__(self):
        super().__init__()
        self.kind: str = "monster"
        self.blocked_by: list[str] = ["wall", "player"]
        self.cannot_share_tile_with: list[str] = ["wall", "monster", "player"]
        self.ignores: list[str] = ["pickable", "light"]  # token_kind or token_species, not both

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

    @property
    def can_dodge(self) -> bool:
        """
        Determines if the Monster can dodge depending on its dodging_ability and the nearby spaces
        :return: True if the Monster is able to dodge, False otherwise
        """
        nearby_spaces = self.get_dungeon().get_nearby_spaces(self.get_position(), self.cannot_share_tile_with)
        return randint(1, 10) + (4 - len(nearby_spaces)) <= self.stats.dodging_ability

    def move_token_or_behave(self, path: list[tuple]) -> None:
        """
        Handles the logic dictating if a Monster should move to a new Tile or behave one the current Tile
        :param path: path to target
        :return: None
        """
        if len(path) == 1:
            self.act_on_tile(self.token.get_current_tile())
        else:
            self.token.slide(path, self.token.on_move_completed)

    def act_on_tile(self, tile: Tile) -> None:
        """
        Manages behavior of Monsters upon landing (or staying) on a Tile
        :param tile: Tile where behavios happens
        :return: None
        """
        self.attack_players()
        self.get_dungeon().game.update_switch("character_done")

    def attack_players(self) -> None:
        """
        Manages attack of monsters to surrounding players
        :return:None
        """
        surrounding_tiles = [self.token.dungeon.get_tile(position)
                             for position in self.token.dungeon.get_nearby_positions(self.get_position())]

        for tile in surrounding_tiles:
            if self.stats.remaining_moves == 0:
                break
            if tile.has_token("player"):
                self.fight_on_tile(tile)

    def fight_on_tile(self, opponent_tile: Tile) -> None:
        """
        Specific fighting method for monsters
        :param opponent_tile: Tile where opponent is located
        :return: None
        """
        opponent = opponent_tile.get_token("player").character
        opponent = self.fight_opponent(opponent)
        opponent.token.bar_length = (
                opponent.stats.health / opponent.stats.natural_health
        )

        if opponent.stats.health <= 0:
            opponent.kill_character(opponent_tile)

    def _find_random_target(self, steps: int) -> tuple[int,int] | None:
        """
        Finds a random free tile within a range of steps
        :return: random free position in range (if any), otherwise None
        """
        free_positions: set[tuple[int,int]] = self.get_dungeon().scan_tiles(self.cannot_share_tile_with, exclude=True)

        reach_free_positions = {position for position in self.get_dungeon().get_range(self.get_position(), steps)
                         if len(self.get_dungeon().find_shortest_path(
                self.get_position(), position, self.blocked_by)) > 1
                                and position in free_positions}

        return choice(list(reach_free_positions)) if len(reach_free_positions) > 0 else None


    def get_random_path(self, max_dist: int) -> list[tuple[int,int]]:
        """
        Generates a path aiming to a random target position at a distance max_dist or less
        from Character.position
        :param max_dist: maximum distance within which the random target must be set
        :return: path to the target. If no target, returns [self.position]
        """
        target: tuple[int,int] = self._find_random_target(max_dist)
        if target is None:
            return [self.get_position()]

        path: list[tuple[int,int]] = self.get_dungeon().find_shortest_path(
            self.get_position(), target, self.blocked_by)

        return path


    def _find_possible_targets(self) -> set[tuple[int,int]]:
        """
        Returns a set with the positions of all possible targets in the dungeon
        :return: set with target coordinates
        """
        target_tokens: set[Token] = {self.get_dungeon().get_tile(position).get_token(self.chases)
                                    for position in self.get_dungeon().scan_tiles([self.chases])}
        return {token.position for token in target_tokens if token.character is None or not token.character.is_hidden}

    def _find_target_by_distance(self) -> tuple[int,int] | None:
        """
        Returns the position of the closest target by straight distance
        :return: coordinates of the position of the target. None if there is no valid target
        """
        targets: set [tuple[int,int]] = self._find_possible_targets()
        targets_and_distances = {target: self.get_dungeon().get_distance(self.get_position(), target)
                                 for target in targets}
        return min(targets_and_distances, key=targets_and_distances.get) if len(targets_and_distances) > 0 else None


    def _find_target_by_path(self) -> tuple[int,int] | None:
        """
        Returns the position of the closest target by path length (it considers blocking obstacles)
        :return: coordinates of the position of the target. None if there is no accessible target
        """
        targets: set[tuple[int,int]] = self._find_possible_targets()
        paths = [self.get_dungeon().find_shortest_path(self.get_position(), target, self.blocked_by)
                 for target in targets]
        sorted_paths = sorted([path for path in paths if len(path) > 1], key=len)
        return sorted_paths[0][-1] if len(sorted_paths) > 0 else None


    def _find_closest_accesses(self, target: tuple[int,int]) -> set[tuple[int,int]] | None:
        """
        Returns the position of the free tile (without any Token.kind of Monster.cannot_share_tile_with)
        closest to the target
        :param target: coordinates of the target
        :return: list with the coordinates of the closest accesses, None if there is no access
        """
        paths_to_access_candidates: list[list[tuple]] = [self.get_dungeon().find_shortest_path
                                                        (target, position, self.blocked_by)
                                                        for position in self.get_dungeon().scan_tiles
                                                        (self.cannot_share_tile_with, exclude=True)]

        # only considered access candidates with valid paths
        # of equal or shorter length than from self.token.position to target
        paths_to_access_candidates = [path for path in paths_to_access_candidates
                                      if 1 < len(path) <= len(self.get_dungeon().find_shortest_path
                                      (self.get_position(), target, self.blocked_by))]

        accesses = set()
        if len(paths_to_access_candidates) > 0:
            shortest_length = min(len(path) for path in paths_to_access_candidates)
            accesses = {path[-1] for path in paths_to_access_candidates if len(path) == shortest_length}

        return accesses if len(accesses) > 0 else None


    def get_path_to_target(self, target: tuple[int,int], smart:bool) -> list[tuple]:
        """
        Finds a path to a target position
        :param target: coordinates of the target position
        :param smart: if True, the entire path to target is returned. If False, it is returned a section of
        the path until a step brings apart the Character from the target (only steps reducing distance allowed)
        :return: path to target (if any), otherwise [Character.position]
        """
        accesses: set[tuple[int,int]] | None = self._find_closest_accesses(target)

        paths_to_accesses: list = []
        if accesses is not None:
            paths_to_accesses: list[list[tuple]] =[self.get_dungeon().find_shortest_path
                                                   (self.get_position(), access, self.blocked_by)
                                                   for access in accesses]
            paths_to_accesses = [path for path in paths_to_accesses if len(path) > 1]

        if len(paths_to_accesses) == 0:
            return [self.get_position()]

        path = sorted(paths_to_accesses, key=len)[0]

        if not smart:
            max_distance = self.get_dungeon().get_distance(self.get_position(), target)
            for idx, position in enumerate(path[1:]):
                current_distance = self.get_dungeon().get_distance(position, target)
                if current_distance > max_distance:
                    path = path[:idx + 1]
                    break
                max_distance = current_distance

        # trim path by movement range
        path = path[:self.stats.remaining_moves + 1]  # first position is self.position
        # remove any landing conflict
        while len(path) > 1 and any(self.get_dungeon().get_tile(path[-1]).has_token(token_kind)
                                    for token_kind in self.cannot_share_tile_with):
            del path[-1]

        return path


# RANDOM MOVEMENT MONSTERS


class Kobold(Monster):
    """
    HIGH movement
    LOW strength
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "K"
        self.name: str = "Kobold"
        self.species: str = "kobold"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.KoboldStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):
        super().move_token_or_behave(self.get_random_path(
            int(self.stats.remaining_moves * self.stats.random_motility)))


class BlindLizard(Monster):
    """
    MEDIUM movement
    MEDIUM strength
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "L"
        self.name: str = "Blind Lizard"
        self.species: str = "lizard"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.BlindLizardStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):
        super().move_token_or_behave(self.get_random_path(
            int(self.stats.remaining_moves * self.stats.random_motility)))


class BlackDeath(Monster):
    """
    VERY HIGH  movement
    VERY HIGH strength
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "B"
        self.name: str = "Black Death"
        self.species: str = "blackdeath"
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.3
        self.stats = stats.BlackDeathStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):
        super().move_token_or_behave(self.get_random_path(
            int(self.stats.remaining_moves * self.stats.random_motility)))


# DIRECT MOVEMENT MONSTERS


class CaveHound(Monster):

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "H"
        self.name: str = "Cave Hound"
        self.species: str = "hound"
        self.step_transition: str = "in_quart"  # gallop
        self.step_duration: float = 0.3
        self.stats = stats.CaveHoundStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):

        target: tuple[int,int] | None = self._find_target_by_path()

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_behave([self.get_position()])
            else:
                super().move_token_or_behave(self.get_path_to_target(target, smart=False))
        else:
            super().move_token_or_behave(self.get_random_path(
                int(self.stats.remaining_moves * self.stats.random_motility)))


class Growl(Monster):
    """
    MEDIUM movement
    HIGH strength
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "G"
        self.name: str = "Growl"
        self.species: str = "growl"
        self.step_transition: str = "in_out_elastic"  # stomping
        self.step_duration: float = 0.7
        self.stats = stats.GrowlStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):

        target: tuple[int, int] | None = self._find_target_by_path()

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_behave([self.get_position()])
            else:
                super().move_token_or_behave(self.get_path_to_target(target, smart=False))
        else:
            super().move_token_or_behave(self.get_random_path(
                int(self.stats.remaining_moves * self.stats.random_motility)))


class RockGolem(Monster):
    """
    LOW movement
    VERY HIGH strength
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "R"
        self.name: str = "Rock Golem"
        self.species: str = "golem"
        self.step_transition: str = "in_out_elastic"  # stomping
        self.step_duration: float = 0.7
        self.stats = stats.RockGolemStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):

        target: tuple[int, int] | None = self._find_target_by_path()

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_behave([self.get_position()])
            else:
                super().move_token_or_behave(self.get_path_to_target(target, smart=False))
        else:
            self.get_dungeon().game.next_character()


# SMART MOVEMENT MONSTERS


class DarkGnome(Monster):
    """
    LOW strength
    MEDIUM movement
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "O"
        self.name: str = "Dark Gnome"
        self.species: str = "gnome"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.DarkGnomeStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):

        target: tuple[int, int] | None = self._find_target_by_path()

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_behave([self.get_position()])
            else:
                super().move_token_or_behave(self.get_path_to_target(target, smart=True))
        else:
            super().move_token_or_behave(self.get_random_path(
                int(self.stats.remaining_moves * self.stats.random_motility)))


class NightMare(Monster):

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "N"
        self.name: str = "Nightmare"
        self.species: str = "nightmare"
        self.step_transition: str = "in_quart"  # gallop
        self.step_duration: float = 0.3
        self.stats = stats.NightmareStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):

        target: tuple[int, int] | None = self._find_target_by_path()

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_behave([self.get_position()])
            else:
                super().move_token_or_behave(self.get_path_to_target(target, smart=True))
        else:
            return super().move_token_or_behave(self.get_random_path(
                int(self.stats.remaining_moves * self.stats.random_motility)))


class LindWorm(Monster):

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "Y"
        self.name: str = "Lindworm"
        self.species: str = "lindworm"
        self.step_transition: str = "in_out_elastic"  # stomping
        self.step_duration: float = 0.7
        self.stats = stats.LindWormStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):

        target: tuple[int, int] | None = self._find_target_by_path()

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_behave([self.get_position()])
            else:
                super().move_token_or_behave(self.get_path_to_target(target, smart=True))
        else:
            self.get_dungeon().game.next_character()


# GHOSTS


class WanderingShadow(Monster):
    """
    RANDOM HIGH movement
    MEDIUM strength
    """
    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "S"
        self.name: str = "Wandering Shadow"
        self.species: str = "shadow"
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.3
        self.stats = stats.WanderingShadowStats()

        self.blocked_by: list = []
        self.cannot_share_tile_with: list[str] = ["monster", "player"]
        self.ignores: list[str] = self.ignores + ["wall"]

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):
        super().move_token_or_behave(self.get_random_path(
            int(self.stats.remaining_moves * self.stats.random_motility)))


class DepthsWisp(Monster):
    """
    DIRECT MEDIUM movement
    LOW strength
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "W"
        self.name: str = "Depths Wisp"
        self.species: str = "wisp"
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.3
        self.stats = stats.DepthsWispStats()

        self.blocked_by: list = []
        self.cannot_share_tile_with: list[str] = ["monster", "player"]
        self.ignores: list[str] = self.ignores + ["wall"]

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):

        target: tuple[int,int] | None = self._find_target_by_distance()

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_behave([self.get_position()])
            else:
                super().move_token_or_behave(self.get_path_to_target(target, smart=False))
        else:
            self.get_dungeon().game.next_character()


class MountainDjinn(Monster):
    """
    DIRECT MEDIUM movement
    HIGH strength
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "D"
        self.name: str = "Mountain Djinn"
        self.species: str = "djinn"
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.3
        self.stats = stats.MountainDjinnStats()

        self.blocked_by: list = []
        self.cannot_share_tile_with: list[str] = ["monster", "player"]
        self.ignores: list[str] = self.ignores + ["wall"]

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self):

        target: tuple[int,int] | None = self._find_target_by_distance()

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_behave([self.get_position()])
            else:
                super().move_token_or_behave(self.get_path_to_target(target, smart=False))
        else:
            self.get_dungeon().game.next_character()


# SPECIAL MONSTERS


class Pixie(Monster):
    """
    HIGH movement
    LOW health
    DOES NOT attack player
    Chases pickables and makes them disappear
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "P"
        self.name: str = "Pixie"
        self.species: str = "pixie"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.stats = stats.PixieStats()

        self.chases: str = "pickable"

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

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

        target: tuple[int, int] | None = self._find_target_by_path()

        if target is not None:
            super().move_token_or_behave(self.get_dungeon().find_shortest_path(self.get_position(), target))
        else:
            super().move_token_or_behave(self.get_random_path(
                int(self.stats.remaining_moves * self.stats.random_motility)))