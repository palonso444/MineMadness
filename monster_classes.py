from __future__ import annotations

from os import remove
from random import randint, choice
from abc import ABC, abstractmethod
from statistics import mean, pvariance

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
        self.attacks_and_retreats: bool = False
        self.invisible: bool = False

        # exclusive of Monster class
        self.chases: str = "player"
        self.acted_on_tile: bool | None = None

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

    @property
    def has_acted(self) -> bool:
        """
        Property defining if a Monster has performed an action this turn (attack, dig, pick object, etc.)
        :return: True if Monser has performed an action, False otherwise
        """
        return self.acted_on_tile

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
        return (any(self.get_dungeon().get_tile(position).has_token(token_species)
             for position in self.get_dungeon().get_nearby_positions(self.get_position()))
         and self.stats.remaining_moves > 0
         and self.stats.remaining_attacks > 0)

    @property
    def can_retreat(self) -> bool:
        """
        Property defining if a Character can retreat after an attack
        :return: True if character can retreat after attack, False otherwise
        """
        return False


    @property
    def can_dodge(self) -> bool:
        """
        Determines if the Monster can dodge depending on its dodging_ability and the nearby spaces
        :return: True if the Monster is able to dodge, False otherwise
        """
        nearby_spaces = self.get_dungeon().get_nearby_spaces(self.get_position(), self.cannot_share_tile_with)
        return randint(1, 10) + (4 - len(nearby_spaces)) <= self.stats.dodging_ability

    @classmethod
    def initialize_moves_attacks(cls) -> None:
        """
        Resets remaining moves and attacks of all Monsters of the class back to the maximum
        :return: None
        """
        super().initialize_moves_attacks()
        for character in cls.data:
            character.stats.remaining_attacks = character.stats.max_attacks
            character.acted_on_tile = False

    def move_token_or_act_on_tile(self, path: list[tuple]) -> None:
        """
        Handles the logic dictating if a Monster should move to a new Tile or act on the current Tile
        :param path: path to target
        :return: None
        """
        if len(path) == 1:
            self.act_on_tile(self.token.get_current_tile())
            if not self.can_retreat:
                self.get_dungeon().game.update_switch("character_done")
        else:
            self.token.slide(path, self.token.on_move_completed)


    def act_on_tile(self, tile: Tile) -> None:
        """
        Manages behavior of Monsters upon landing (or staying) on a Tile
        :param tile: Tile where behavior happens
        :return: None
        """
        if self.can_fight("player"):
            self.attack_players()
            self.acted_on_tile = True


    def attack_players(self) -> None:
        """
        Manages attack of monsters to surrounding players
        :return:None
        """
        if self.stats.remaining_attacks > self.stats.remaining_moves:
            self.stats.remaining_attacks = self.stats.remaining_moves

        surrounding_player_tiles = [
            tile for position in self.get_dungeon().get_nearby_positions(self.get_position())
            if (tile := self.get_dungeon().get_tile(position)).has_token("player")
        ]

        for attack in range(self.stats.remaining_attacks):
            surrounding_player_tiles = [tile for tile in surrounding_player_tiles if tile.has_token("player")]
            if len(surrounding_player_tiles) == 0:
                break
            self.fight_on_tile(choice(surrounding_player_tiles))
            self.stats.remaining_attacks -= 1
            self.stats.remaining_moves -= 1


    def fight_on_tile(self, opponent_tile: Tile) -> None:
        """
        Specific fighting method for monsters
        :param opponent_tile: Tile where opponent is located
        :return: None
        """
        opponent = opponent_tile.get_token("player").character
        opponent = self.fight_opponent(opponent)
        opponent.token.bar_length = opponent.stats.health / opponent.stats.natural_health

        if opponent.stats.health <= 0:
            opponent.kill_character(opponent_tile)


    def find_random_target(self, max_steps: int, min_steps: int | None = None) -> tuple[int,int] | None:
        """
        Finds a random free position within a range of steps
        :param max_steps: max number of steps from self.token.position to the found target
        :param min_steps: min number of steps from self.token.position to the found target
        :return: random free position in range (if any), otherwise None
        """
        free_positions: set[tuple[int,int]] = self.get_dungeon().scan_tiles(self.cannot_share_tile_with, exclude=True)

        reach_free_positions = {position for position in self.get_dungeon().get_range(self.get_position(), max_steps)
                         if self.get_dungeon().check_if_connexion(self.get_position(), position, self.blocked_by, max_steps)
                                and position in free_positions}

        if min_steps is not None:
            reach_free_positions = {position for position in reach_free_positions
                                    if not self.get_dungeon().check_if_connexion
                                    (self.get_position(), position, self.blocked_by, min_steps - 1)}  # min is included

        return choice(list(reach_free_positions)) if len(reach_free_positions) > 0 else None


    def _find_isolated_target(self, steps: int, exclude: str,
                              exclude_blocked_by: list[str] | None = None) -> tuple[int,int] | None:
        """
        Finds a free position as far as possible, within the specified number of steps,
        from the Token.kind specified in exclude
        :param steps: max number of steps from self.token.position to the found target
        :param exclude: Token.kind to avoid
        :param exclude_blocked_by: Token.kinds that block the exclude Token.character (if any)
        :return: free position in range (if any), otherwise None
        """
        free_positions: set[tuple[int,int]] = self.get_dungeon().scan_tiles(self.cannot_share_tile_with, exclude=True)

        reach_free_positions = {position for position in self.get_dungeon().get_range(self.get_position(), steps)
                         if self.get_dungeon().check_if_connexion(self.get_position(), position, self.blocked_by, steps)
                                and position in free_positions}

        if len(reach_free_positions) == 0:
            return None  # exit here so no need of useless expensive computation

        # all positions to avoid are considered, not only the ones in range
        positions_to_avoid = {position for position in self.get_dungeon().scan_tiles([exclude], exclude=False)
                              if len(self.get_dungeon().find_shortest_path
                              (self.get_position(), position, exclude_blocked_by)) > 1}

        if len(positions_to_avoid) == 0:
            raise Exception("There is nothing to flee from!")

        position_stats: dict[tuple[int,int]: list] = {rf_position : [len(self.get_dungeon().find_shortest_path
                                                                        (rf_position, av_position, exclude_blocked_by))
                                                                    for av_position in positions_to_avoid]
                                                      for rf_position in reach_free_positions}

        position_stats = {rf_position: ([mean(position_stats[rf_position]), pvariance(position_stats[rf_position])]
                                         if len(position_stats[rf_position]) > 1
                                         else [position_stats[rf_position][0], 0])
                          for rf_position in position_stats.keys()}

        # suitable positions have the max mean and the min variance (equally far from all excluded Token.kinds)
        max_mean = max(value[0] for value in position_stats.values())
        position_stats = {rf_position: value for rf_position, value in position_stats.items() if value[0] == max_mean}
        min_var = min(value[1] for value in position_stats.values())
        position_stats = {rf_position: value for rf_position, value in position_stats.items() if value[1] == min_var}

        return choice(list(position_stats.keys()))  # None is returned above


    def get_path_to_target(self, target: tuple[int,int] | None) -> list[tuple[int,int]]:
        """
        Generates a path aiming directly to a target from Character.position
        :param target: target position
        :return: path to the target. If target is unreachable, returns [self.position]
        """
        if target is None:
            return [self.get_position()]

        path: list[tuple[int,int]] = self.get_dungeon().find_shortest_path(
            self.get_position(), target, self.blocked_by)

        return path


    def _find_possible_targets(self, free: bool) -> set[tuple[int,int]]:
        """
        Returns a set with the positions of all possible targets in the dungeon
        :param free: bool stating if target must be in a free tile (not shared with Token.kind of
        self.cannot_share_tile_with)
        :return: set with target coordinates
        """
        target_tokens: set[Token] = {self.get_dungeon().get_tile(position).get_token(self.chases)
                                    for position in self.get_dungeon().scan_tiles([self.chases])}
        if free:
            target_tokens: set[Token] = {token for token in target_tokens if
                                         not any(self.get_dungeon().get_tile(token.position).has_token(token_kind)
                                                 for token_kind in self.cannot_share_tile_with)}
        return {token.position for token in target_tokens if token.character is None or not token.character.is_hidden}


    def _find_target_by_distance(self, targets: set[tuple[int,int]]) -> tuple[int,int] | None:
        """
        Returns the position of the closest target by straight distance
        :param targets: set of candidate target positions to evaluate
        :return: coordinates of the position of the target. None if there is no valid target
        """
        targets_and_distances = {target: self.get_dungeon().get_distance(self.get_position(), target)
                                 for target in targets}
        return min(targets_and_distances, key=targets_and_distances.get) if len(targets_and_distances) > 0 else None


    def _find_target_by_path(self, targets: set[tuple[int,int]]) -> tuple[int,int] | None:
        """
        Returns the position of the closest target by path length (it considers blocking obstacles)
        :param targets: set of candidate target positions to evaluate
        :return: coordinates of the position of the target. None if there is no accessible target
        """
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

        # only considered access candidates with valid paths to target
        # of equal or shorter length than from self.token.position to target
        paths_to_access_candidates = [path for path in paths_to_access_candidates
                                      if 1 < len(path) <= len(self.get_dungeon().find_shortest_path
                                      (self.get_position(), target, self.blocked_by))]

        #exclude inaccessible access candidates from current position
        paths_to_access_candidates = [path for path in paths_to_access_candidates
                                      if len(self.get_dungeon().find_shortest_path
                                      (self.get_position(), path[-1], self.blocked_by)) > 1]

        accesses = set()
        if len(paths_to_access_candidates) > 0:
            shortest_length = min(len(path) for path in paths_to_access_candidates)
            accesses = {path[-1] for path in paths_to_access_candidates if len(path) == shortest_length}

        return accesses if len(accesses) > 0 else None


    def _select_path_to_target(self, accesses: set[tuple[int,int]] | None,
                               direct_to_target: tuple[int,int] | None = None) -> list[tuple]:
        """
        Finds the best path to a target position
        :param accesses: coordinates of the closest accesses to target position
        :param direct_to_target: position of the target (optional). If passed, only path that brings the Character
        closer to the target is returned (only steps reducing distance allowed). Otherwise, the entire path is returned
        :return: path to target (if any), otherwise [Character.position]
        """
        paths_to_accesses: list = []
        if accesses is not None:
            paths_to_accesses: list[list[tuple]] =[self.get_dungeon().find_shortest_path
                                                   (self.get_position(), access, self.blocked_by)
                                                   for access in accesses]
            paths_to_accesses = [path for path in paths_to_accesses if len(path) > 1]

        if len(paths_to_accesses) == 0:
            return [self.get_position()]

        path = sorted(paths_to_accesses, key=len)[0]
        if direct_to_target is not None:
            max_distance = self.get_dungeon().get_distance(self.get_position(), direct_to_target)
            for idx, position in enumerate(path[1:]):
                current_distance = self.get_dungeon().get_distance(position, direct_to_target)
                if current_distance > max_distance:
                    path = path[:idx + 1]
                    break
                max_distance = current_distance

        path = path[:self.stats.remaining_moves + 1]  # first position is self.position
        path = self._remove_landing_conflicts(path)

        return path

    def _remove_landing_conflicts(self, path: list[tuple]) -> list[tuple]:
        """
        Removed positions starting from the end of the path where Monster cannot land until a suitable position is found
        :param path: path to check
        :return: trimmed path
        """
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
        super().move_token_or_act_on_tile(self.get_path_to_target(
            self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


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
        super().move_token_or_act_on_tile(self.get_path_to_target(
            self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


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
        super().move_token_or_act_on_tile(self.get_path_to_target(
            self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


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

        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                super().move_token_or_act_on_tile(self._select_path_to_target(accesses, direct_to_target=target))
        else:
            super().move_token_or_act_on_tile(self.get_path_to_target(
                self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


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

        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                super().move_token_or_act_on_tile(self._select_path_to_target(accesses, direct_to_target=target))
        else:
            super().move_token_or_act_on_tile(self.get_path_to_target(
                self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


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

        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                super().move_token_or_act_on_tile(self._select_path_to_target(accesses, direct_to_target=target))
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

        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                super().move_token_or_act_on_tile(self._select_path_to_target(accesses))
        else:
            super().move_token_or_act_on_tile(self.get_path_to_target(
                self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


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

        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                super().move_token_or_act_on_tile(self._select_path_to_target(accesses))
        else:
            super().move_token_or_act_on_tile(self.get_path_to_target(
                self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


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

        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                super().move_token_or_act_on_tile(self._select_path_to_target(accesses))
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
        super().move_token_or_act_on_tile(self.get_path_to_target(
            self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


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

        target: tuple[int,int] | None = self._find_target_by_distance(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                super().move_token_or_act_on_tile(self._select_path_to_target(accesses, direct_to_target=target))
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

        target: tuple[int,int] | None = self._find_target_by_distance(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                super().move_token_or_act_on_tile(self._select_path_to_target(accesses, direct_to_target=target))
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
            self.acted_on_tile = True
        super().act_on_tile(tile)

    def move(self):

        targets: set[tuple[int, int]] = self._find_possible_targets(free=True)

        if len(targets) > 0:
            super().move_token_or_act_on_tile(self._select_path_to_target(targets))
        else:
            super().move_token_or_act_on_tile(self.get_path_to_target(
                self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))

class RattleSnake(Monster):
    """
    HIGH movement
    Attacks player once and tries to escape
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "V"
        self.name: str = "Rattlesnake"
        self.species: str = "rattlesnake"
        self.step_transition: str = "linear"  # sliding
        self.step_duration: float = 0.4
        self.stats = stats.RattleSnakeStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)


    @property
    def can_retreat(self) -> bool:
        """
        Property defining if a Character can retreat after an attack
        :return: True if character can retreat after attack, False otherwise
        """
        return self.has_acted and self.stats.remaining_moves > 0


    def attack_players(self) -> None:
        """
        Attacks and retreats
        :return: None
        """
        super().attack_players()
        path: list[tuple[int,int]] = (self.get_path_to_target(self._find_isolated_target(
            self.stats.remaining_moves, self.chases, ["wall"])))
        self.token.slide(path, self.token.on_retreat_completed)   # no check if path > 1. It must always be so


    def move(self):

        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                # only consider accesses if next to player and close enough to monster
                # to retrieve after attack
                accesses: set = {access for access in self._find_closest_accesses(target)
                                 if self.get_dungeon().are_nearby(access, target)
                                 and self.get_dungeon().check_if_connexion
                                 (self.get_position(), access,
                                  self.blocked_by, self.stats.remaining_moves // randint(2,4))}
                if len(accesses) == 0:
                    self.get_dungeon().game.next_character()
                else:
                    super().move_token_or_act_on_tile(self._select_path_to_target(accesses))
        else:
            super().move_token_or_act_on_tile(self.get_path_to_target(
                self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))


class Penumbra(Monster):
    """
    HIGH movement
    Attacks player once and tries to escape
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "A"
        self.name: str = "Penumbra"
        self.species: str = "penumbra"
        self.step_transition: str = "in_out_quad"  # walking
        self.step_duration: float = 0.35
        self.invisible = True
        self.stats = stats.PenumbraStats()

        # exclusive of penumbra
        self.ability_active: bool = False

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)


    @property
    def can_retreat(self) -> bool:
        """
        Property defining if a Character can retreat after an attack. Penumbra.stats.remaining_moves
        are set to 0 when it cannot reach any player with enough remaining moves to attack and retreat
        :return: True if character can retreat after attack, False otherwise
        """
        return self.has_acted and self.stats.remaining_moves > 0


    @property
    def is_hidden(self) -> bool:
        """
        Determines if the Monster is hidden
        :return: True if hidden, False otherwise
        """
        return self.ability_active

    def hide_if_player_in_range(self, steps: int, position: tuple[int,int] | None = None) -> None:
        """
        Hides if there is a player within reachable range a Player within reachable range
        :param steps: range within which the Player must be
        :param position: position from which the steps should be counted (optional)
        :return: None
        """
        player_positions = {tile.position for tile in self.get_dungeon().children if tile.has_token("player")}
        position = self.get_position() if position is None else position

        if any(self.get_dungeon().check_if_connexion(position, player_position,
                                       self.blocked_by,
                                       steps)
               for player_position in player_positions):
            self.hide()

    def hide(self) -> None:
        """
        Hides the Monster
        :return: None
        """
        self.token.color.a = 0.5  # changes transparency
        self.ability_active = True

    def unhide_if_all_players_unreachable(self) -> None:
        """
        Unhides the Monster if all players are unreachable (no possible path to them)
        :return: None
        """
        player_positions = {tile.position for tile in self.get_dungeon().children if tile.has_token("player")}

        if all(len(self.get_dungeon().find_shortest_path(self.get_position(),
                                                         player_position,
                                                         self.blocked_by)) == 1
               for player_position in player_positions):
            self.unhide()

    def unhide(self) -> None:
        """
        Unhides the Monster
        :return: None
        """
        self.token.color.a = 1  # changes transparency
        self.ability_active = False

    def attack_players(self) -> None:
        """
        Attacks and retreats
        :return: None
        """
        #if any(self.get_dungeon().get_tile(position).has_token("player")
               #for position in self.get_dungeon().get_nearby_positions(self.get_position())):

        super().attack_players()

        path: list[tuple[int,int]] = (self.get_path_to_target(self.find_random_target(
            max_steps=self.stats.remaining_moves, min_steps=self.stats.min_retreat_dist)))
        if len(path) > 1:
            self.token.slide(path, self.token.on_retreat_completed)
        else:  # if somehow cannot retreat will stay in place
            self.stats.remaining_moves = 0

        #else:
            #self.stats.remaining_moves = 0  # no retreat if no attack happened



    def move(self):

        self.unhide_if_all_players_unreachable()

        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                path: list[tuple] = self._select_path_to_target(self._find_closest_accesses(target))

                max_dist: int = self.stats.remaining_moves - self.stats.max_attacks - self.stats.min_retreat_dist
                max_dist = 0 if max_dist < 0 else max_dist
                distance_to_target: int = len(self.get_dungeon().find_shortest_path(self.get_position(), target)) - 1
                # penumbra does not get too close to player. It ensures max_attacks and retreat moves
                # if still far, will approach full movement
                if len(path) > max_dist + 1 and distance_to_target < (max_dist * 2 + 1):
                    path = self._remove_landing_conflicts(path[:max_dist + 1])

                super().move_token_or_act_on_tile(path)

        else:
            super().move_token_or_act_on_tile(self.get_path_to_target(
                self.find_random_target(int(self.stats.remaining_moves * self.stats.random_motility))))

class ClawJaw(Monster):
    """
    Chases players and destroys walls if any on the way.
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "C"
        self.name: str = "Claw Jaw"
        self.species: str = "clawjaw"
        self.blocked_by: list | None = None  # values vary in _set_possible_targets() and self.move()
        self.cannot_share_tile_with: list[str] | None = None  # values vary in _set_possible_targets() and self.move()
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.4
        self.stats = stats.ClawJawStats()

        # exclusive of claw jaw
        self.dig_position: tuple[int,int] | None = None  # position of the wall to dig
        self.dig_factor: float = 0.75  # the higher, the higher the chance of taking digging path if free available

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        """
        Determines if a Character is able to dig a certain kind of wall
        :param token_species: Token.species of the wall Token
        :return: True if can dig, False otherwise
        """
        match token_species:
            case "rock":
                return self.stats.remaining_moves >= 1
            case "granite":
                return self.stats.remaining_moves >= 3
            case "quartz":
                return self.stats.remaining_moves == self.stats.moves
            case _:
                raise ValueError(f"Invalid token_species {token_species}")


    def act_on_tile(self, tile: Tile) -> None:
        """
        Digs walls, if required. Afterwards acts just as any other monster
        :param tile: Tile on which to act
        :return: None
        """
        if self.dig_position is not None:
            tile_to_dig = self.get_dungeon().get_tile(self.dig_position)
            self.dig_position = None
            if self.can_dig(tile_to_dig.get_token("wall").species):
                self.dig(tile_to_dig)
                self.acted_on_tile = True

        super().act_on_tile(tile)

    def stop_upon_wall(self, path: list[tuple]) -> tuple[list, tuple | None]:
        """
        Trims the path until the first wall is found so monster will stop right in front of it
        :param path: whole path
        :return: the trimmed path and the wall position (if any) otherwise the whole path
        """
        for idx, position in enumerate(path):
            if self.get_dungeon().get_tile(position).has_token("wall"):
                return path[:idx], path[idx]
        return path, None


    def dig(self, wall_tile: Tile) -> None:
        """
        Digging method for Claw Jaw
        :param wall_tile: Tile upon which the digging must be performed
        :return: None
        """
        match wall_tile.get_token("wall").species:
            case "rock":
                self.stats.remaining_moves -= 1
            case "granite":
                self.stats.remaining_moves -= 2
            case "quartz":
                self.stats.remaining_moves = 0

        wall_tile.get_token("wall").show_digging()
        wall_tile.get_token("wall").delete_token(wall_tile)

        if wall_tile.has_token("light"):
            while len(wall_tile.tokens["light"]) > 0:
                wall_tile.get_token("light").delete_token(wall_tile)
            self.get_dungeon().update_bright_spots()

    def _move_across_walls(self, target: tuple[int,int]) -> None:
        """
        This method allows the Claw Jaw to chase a target going across walls and stopping
        when encountering one
        :param target: target position to reach
        :return: None
        """
        self.blocked_by, self.cannot_share_tile_with = ["player"], ["monster", "player"]
        path, wall_position = self.stop_upon_wall(self._select_path_to_target
                                                  (self._find_closest_accesses(target)))

        self.dig_position: tuple[int, int] | None = wall_position
        super().move_token_or_act_on_tile(path)

    def _set_possible_targets(self) -> tuple:
        """
        This method finds two possible targets at once, one by distance and the other by path
        :return: coordinates of the target by distance, coordinates of the target by path
        """
        self.cannot_share_tile_with: list[str] = ["monster", "player"]
        target_dist: tuple[int, int] | None = self._find_target_by_distance(self._find_possible_targets(free=False))

        self.blocked_by, self.cannot_share_tile_with = ["wall", "player"], ["wall", "monster", "player"]
        target_path: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        return target_dist, target_path

    def move(self):

        target_dist, target_path = self._set_possible_targets()

        if target_path is None and target_dist is None:
            self.get_dungeon().game.next_character()
        elif self.get_dungeon().are_nearby(self.get_position(), target_dist):
            super().move_token_or_act_on_tile([self.get_position()])
        elif target_path is None:
            self._move_across_walls(target_dist)
        else:
            self.blocked_by, self.cannot_share_tile_with = ["wall", "player"], ["wall", "monster", "player"]
            path: list[tuple] = self._select_path_to_target(self._find_closest_accesses(target_path))
            # if path too long, will go across walls
            if len(path) * self.dig_factor > self.get_dungeon().get_distance(self.get_position(), target_dist):
            # if (len(path) == 1 or
                # len(path) > self.get_dungeon().get_distance(self.get_position(), target_dist) * 2.5):
                self._move_across_walls(target_dist)
            else:
                super().move_token_or_act_on_tile(path)
