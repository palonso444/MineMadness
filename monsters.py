from __future__ import annotations
from monster_classes import Monster
import game_stats as stats

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

    def move(self) -> None:
        super().move_randomly()


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

    def move(self) -> None:
        super().move_randomly()


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

    def move(self) -> None:
        super().move_randomly()

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

    def move(self) -> None:
        super().chase(smart=False)


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

    def move(self) -> None:
        super().chase(smart=False)


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

    def move(self) -> None:
        super().chase(smart=False)

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

    def move(self) -> None:
        super().chase(smart=True)


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

    def move(self) -> None:
        super().chase(smart=True)


class LindWorm(Monster):

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "Y"
        self.name: str = "Lindworm"
        self.species: str = "lindworm"
        self.step_transition: str = "in_out_elastic"  # stomping
        self.step_duration: float = 0.55
        self.stats = stats.LindWormStats()

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def move(self) -> None:
        super().chase(smart=True)

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

    def move(self) -> None:
        super().move_randomly()


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

    def move(self) -> None:
        super().chase(smart=False)


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

    def move(self) -> None:
        super().chase(smart=False)

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

    def move(self) -> None:
        """
        Special method for picking up objects, if no object left, move randomly
        :return:
        """
        targets: set[tuple[int, int]] = self._find_possible_targets(free=True)

        if len(targets) > 0:
            super().move_token_or_act_on_tile(self._select_path_to_target(targets))
        else:
            super().move_randomly()

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
        return self.has_acted and self.remaining_moves > 0

    def attack_players(self) -> None:
        """
        Attacks and retreats
        :return: None
        """
        super().attack_players()
        path: list[tuple[int,int]] = (self.get_path_to_target(self._find_isolated_target(
            self.remaining_moves, self.chases, ["wall"])))
        if len(path) > 1:  # if all players dead, no path
            self.token.slide(path, self.token.on_retreat_completed)
        else:  # if it cannot retreat will stay in place
            # self.remaining_moves = 0
            self.token.steps = self.remaining_moves

    def move(self) -> None:
        """
        Special method for attack only if enough movements left to retreat
        :return: None
        """
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
                                  self.blocked_by, self.remaining_moves // randint(2,4))}
                if len(accesses) == 0:
                    self.get_dungeon().game.activate_next_character()
                else:
                    super().move_token_or_act_on_tile(self._select_path_to_target(accesses))
        else:
            super().move_randomly()


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
        Property defining if a Character can retreat after an attack. Penumbra.remaining_moves
        are set to 0 when it cannot reach any player with enough remaining moves to attack and retreat
        :return: True if character can retreat after attack, False otherwise
        """
        return self.has_acted and self.remaining_moves > 0

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
        self.token.color.a = 0  # changes transparency
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
            max_steps=self.remaining_moves, min_steps=self.stats.min_retreat_dist)))
        if len(path) > 1:
            self.token.slide(path, self.token.on_retreat_completed)
        else:  # if it cannot retreat will stay in place
            #self.remaining_moves = 0
            self.token.steps = self.remaining_moves

    def move(self):
        """
        Special method for hiding and attacking
        :return: None
        """
        self.unhide_if_all_players_unreachable()
        target: tuple[int, int] | None = self._find_target_by_path(self._find_possible_targets(free=False))

        if target is not None:
            if self.get_dungeon().are_nearby(self.get_position(), target):
                super().move_token_or_act_on_tile([self.get_position()])
            else:
                path: list[tuple] = self._select_path_to_target(self._find_closest_accesses(target))

                max_dist: int = self.remaining_moves - self.stats.max_attacks - self.stats.min_retreat_dist
                max_dist = 0 if max_dist < 0 else max_dist
                distance_to_target: int = len(self.get_dungeon().find_shortest_path(self.get_position(), target)) - 1
                # penumbra does not get too close to player. It ensures max_attacks and retreat moves
                # if still far, will approach full movement
                if len(path) > max_dist + 1 and distance_to_target < (max_dist * 2 + 1):
                    path = self._remove_landing_conflicts(path[:max_dist + 1])

                super().move_token_or_act_on_tile(path)

        else:
            super().move_randomly()


class ClawJaw(Monster):
    """
    Chases players and destroys walls if any on the way.
    """
    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "C"
        self.name: str = "Claw Jaw"
        self.species: str = "clawjaw"
        # values of self.blocked_by vary in _set_possible_targets() and self.move() and self._move_across walls
        # values self.cannot_share_tile_with vary in _set_possible_targets() and self.move() self._move_across walls
        self.step_transition: str = "linear"  # gliding
        self.step_duration: float = 0.4
        self.stats = stats.ClawJawStats()

        # exclusive of claw jaw
        self.dig_position: tuple[int,int] | None = None  # position of the wall to dig
        self.dig_factor: float = 0.75  # the higher, the higher the chance of taking digging path if free available

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def restore_cannot_share_blocked_by(self) -> None:
        """
        Resets default values for Monster.cannot_share_tile_with and Monster.blocked_by
        :return: None
        """
        self.blocked_by = ["wall", "player"]
        self.cannot_share_tile_with = ["wall", "monster", "player"]

    def can_dig(self, token_species: str) -> bool:
        """
        Determines if a Character is able to dig a certain kind of wall
        :param token_species: Token.species of the wall Token
        :return: True if can dig, False otherwise
        """
        match token_species:
            case "rock":
                return self.remaining_moves >= 1
            case "granite":
                return self.remaining_moves >= 3
            case "quartz":
                return self.remaining_moves == self.stats.moves
            case _:
                raise ValueError(f"Invalid token_species {token_species}")


    def act_on_tile(self, tile: Tile) -> None:
        """
        Digs walls, if required. Afterward acts just as any other monster
        :param tile: Tile on which to act
        :return: None
        """
        if self.dig_position is not None:
            tile_to_dig = self.get_dungeon().get_tile(self.dig_position)
            self.dig_position = None
            if self.can_dig(tile_to_dig.get_token("wall").species):
                self.dig(tile_to_dig)
                self.acted_on_tile = True

        self.restore_cannot_share_blocked_by()
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
                # self.remaining_moves -= 1
                self.token.steps += 1
            case "granite":
                # self.remaining_moves -= 3
                self.token.steps += 3
            case "quartz":
                # self.remaining_moves = 0
                self.token.steps = self.remaining_moves

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

    def move(self) -> None:
        """
        Special method for moving across walls
        :return: None
        """
        target_dist, target_path = self._set_possible_targets()

        if target_path is None and target_dist is None:
            self.get_dungeon().game.activate_next_character()
        elif self.get_dungeon().are_nearby(self.get_position(), target_dist):
            super().move_token_or_act_on_tile([self.get_position()])
        elif target_path is None:
            self._move_across_walls(target_dist)
        else:
            self.blocked_by, self.cannot_share_tile_with = ["wall", "player"], ["wall", "monster", "player"]
            path: list[tuple] = self._select_path_to_target(self._find_closest_accesses(target_path))

            # if path too long, will go across walls
            if len(path) * self.dig_factor > self.get_dungeon().get_distance(self.get_position(), target_dist):
                self._move_across_walls(target_dist)
            else:
                super().move_token_or_act_on_tile(path)
