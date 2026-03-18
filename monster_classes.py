from __future__ import annotations

from random import randint, choice
from abc import ABC, abstractmethod
from statistics import mean, pvariance

from character_class import Character


class Monster(Character, ABC):

    # those lists are initialized before kivy even starts
    data: list[Character] = []

    def __init__(self):
        super().__init__()
        self.kind: str = "monster"
        self.blocked_by: list[str] = ["wall", "player"]
        self.cannot_share_tile_with: list[str] = ["wall", "monster", "player"]
        self.ignores: list[str] = ["pickable", "light", "treasure"]  # token_kind or token_species
        self.attacks_and_retreats: bool = False
        self.invisible: bool = False
        self.inventory: dict[str,int] = {
            "jerky": 0,
            "coffee": 0,
            "tobacco": 0,
            "whisky": 0,
            "talisman": 0
        }  # placeholder needed for MineMadnessGame update_inventory_interface(). Must not be updated!

        # exclusive of Monster class
        self.chases: str = "player"
        self.acted_on_tile: bool = False

    @abstractmethod
    def move(self):
        pass

    def setup_character(self, game: MineMadnessGame) -> None:
        """
        Sets up the character when it first enters the game
        :return: None
        """
        super().setup_character(game)
        self.stats.remaining_attacks = 0

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


    def can_fight(self, token_kind: str) -> bool:
        """
        Determines if a monster can fight a specific token_kind
        :param token_kind: Token.kind of the opponent
        :return: True if the Monster can fight, False otherwise
        """
        return (any(self.get_dungeon().get_tile(position).has_token(token_kind)
             for position in self.get_dungeon().get_nearby_positions(self.get_position()))
         and self.remaining_moves > 0
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
    def reset_moves(cls) -> None:
        """
        Resets remaining moves and attacks of all Monsters of the class back to the maximum
        :return: None
        """
        for character in cls.data:
            if character.state == "in_game":
                character.remaining_moves = character.stats.moves
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
            self.token.skip_moves()  # if monster is blocked, this triggers next monster
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
        if self.stats.remaining_attacks > self.remaining_moves:
            self.stats.remaining_attacks = self.remaining_moves

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
            self.token.steps += 1

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
            return None
            #raise Exception("There is nothing to flee from!")

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

        path = path[:self.remaining_moves + 1]  # first position is self.position
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

    #######################################################################################################
    ##                                   PRE-DEFINED MONSTER MOVEMENT PATTERNS                           ##
    #######################################################################################################

    def move_randomly(self) -> None:
        """
        Moves randomly, does not chase anything
        :return: None
        """
        self.move_token_or_act_on_tile(self.get_path_to_target(
            self.find_random_target(int(self.remaining_moves * self.stats.random_motility))))

    def chase(self, smart: bool) -> None:
        """
        Chases whatever Token.kind has in Monster.chases
        :param smart: if True, it goes around obstacles in a smart way. Otherwise it nevers moves away from target,
        so it gets blocked by walls if cannot move forward
        :return: None
        """
        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                self.move_token_or_act_on_tile([self.get_position()])
            else:
                accesses = self._find_closest_accesses(target)
                if smart:
                    self.move_token_or_act_on_tile(self._select_path_to_target(accesses))
                else:
                    self.move_token_or_act_on_tile(self._select_path_to_target(accesses, direct_to_target=target))
        else:
            self.move_token_or_act_on_tile(self.get_path_to_target(
                self.find_random_target(int(self.remaining_moves * self.stats.random_motility))))

