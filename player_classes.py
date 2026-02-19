from __future__ import annotations
from abc import ABC, abstractmethod
from random import random

from kivy.properties import NumericProperty

from character_class import Character
import game_stats as stats
from dungeon_classes import DungeonLayout


class Player(Character, ABC):

    experience = NumericProperty(0)
    player_level = NumericProperty(1)
    shovels = NumericProperty(0)
    weapons = NumericProperty(0)

    # this is the starting order as defined by Player.set_starting_player_order()
    chars: tuple[str,str,str] = ("%", "?", "&")  # % sawyer, ? hawkins, & crusher jane
    data: list[Character] = []
    in_game: list[int] = []
    dead: list[int] = []
    exited: list[int] = []
    gems: int = 0

    @classmethod
    def clear_character_data(cls) -> None:
        """
        Removes all characters from the game but keeps Player.data intact
        :return: None
        """
        cls.in_game.clear()
        cls.dead.clear()
        cls.exited.clear()

    @classmethod
    def setup_player_data_and_ids(cls) -> None:
        """
        Sets up player data
        :return: None
        """
        cls._set_player_order()
        cls._set_ids()

    @classmethod
    def _set_ids(cls) -> None:
        """
        Sets the ids of the Players according to their index in Player.data
        :return: None
        """
        for player in Player.data:
            player.id = player.data.index(player)

    @classmethod
    def _set_player_order(cls) -> None:
        """
        Sets the starting player turn order: Sawyer, Hawkins, Crusher Jane
        :return: None
        """
        sawyer = next((player for player in Player.data if isinstance(player, Sawyer)), None)
        hawkins = next((player for player in Player.data if isinstance(player, Hawkins)), None)
        jane = next((player for player in Player.data if isinstance(player, CrusherJane)), None)
        Player.data = [sawyer, hawkins, jane]

    @classmethod
    def all_players_alive(cls):
        return len(cls.in_game) == len(cls.data)

    @classmethod
    def all_players_dead(cls):
        return len(cls.dead) == len(cls.data)

    @classmethod
    def check_if_dead(cls, player_species: str) -> bool:
        """
        Checks if a particular Player is dead
        :param player_species: Player.species of the player to check
        :return: True if dead, False otherwise
        """
        return any(Player.get_from_data(player_id).species == player_species for player_id in cls.dead)

    @classmethod
    def get_surviving_player_chars(cls) -> list[str]:
        """
        Returns the players that survived the level
        :return: set or tuple containing the characters representing live players
        """
        if len(Player.exited) > 0:
            return [Player.get_from_data(player_id).char for player_id in cls.exited]
        else:
            return list(Player.chars)

    @classmethod
    def check_if_all_players_out(cls, game) -> None:
        """
        Checks if all players out and acts consequently
        :return: None
        """
        if cls.all_out():
            game.finish_level()
        else:
            game.activate_next_character()


    def __init__(self):
        super().__init__()
        self.kind: str = "player"
        self.blocked_by: list[str] = ["wall", "monster", "trap"]
        self.cannot_share_tile_with: list[str] = ["wall", "monster", "player"]
        self.ignores: list[str] = ["light"]
        self.invisible: bool = False
        self.step_transition: str = "in_out_quad" # walking
        self.step_duration: float = 0.35

        # attributes exclusive of Player class
        self.inventory: dict[str,int] = {
            "jerky": 2,
            "coffee": 0,
            "tobacco": 0,
            "whisky": 0,
            "talisman": 0,
        }
        self.effects: dict[str,list] = {"moves": [], "toughness": [], "strength": []}
        self.state: str | None = None
        self.special_items: dict[str,int] | None = None
        self.ability_active: bool | None = None
        self.level_track: dict[int,dict] = dict()

        self.bind(experience=self.on_experience)
        self.bind(player_level=self.on_player_level)

    def setup_character(self, game: MineMadnessGame) -> None:
        """
        Sets up the character when it first enters the game
        :return: None
        """
        self.game = game
        self.__class__.data.append(self)
        self.shovels = self.stats.initial_shovels
        self.weapons = self.stats.initial_weapons

    def setup_for_new_level(self) -> None:
        """
        Sets up the Player to start a new level (not level 1)
        :return: None
        """
        self.heal(self.stats.recovery_end_of_level)
        self.ability_active = False

    @staticmethod
    def on_shovels(player: Player, value: int) -> None:
        """
        Notifies the game when a shovel is used or picked up
        :param player: instance of the Player
        :param value: new shovels value
        :return: None
        """
        player.game.update_label("shovels_label", value)

    @staticmethod
    def on_weapons(player: Player, value: int):
        """
        Notifies the game when a weapon is used or picked up
        :param player: instance of the Player
        :param value: new weapon value
        :return: None
        """
        player.game.update_label("weapons_label", value)

    @abstractmethod
    def on_player_level(self, instance: Player, value: int) -> None:
        """
        Logic of levelling up
        :param instance: instance of the player
        :param value: new level
        :return: None
        """
        pass

    @abstractmethod
    def enhance_damage(self, damage: int) -> int:
        """
        Placeholder needed for fight method
        :param damage: damage
        :return: enhanced damage
        """
        pass

    @property
    def has_all_gems(self) -> bool:
        """
        Checks if players have all gems
        :return: True if players have all gems, False otherwise
        """
        return Player.gems == self.get_dungeon().game.total_gems

    def has_item(self, item: str) -> bool:
        """
        Checks if a Player has an item
        :param item: item name to check
        :return: True if has the item, False otherwise
        """
        return self.inventory[item] > 0

    @property
    def is_dead(self) -> bool:
        """
        Checks if the Player is dead
        """
        return self in Player.dead

    @property
    def is_exited(self) -> bool:
        """
        Checks if the Player has exited the level
        :return: True if character is hidden, False otherwise
        """
        return self in Player.exited


    @abstractmethod
    def can_fight(self, token_species: str) -> bool:
        """
        Abstract method defining if the Player fulfills the requirements to fight with an opponent
        represented by a Token of the specified Token.species
        :param token_species: Token.species of the opponent
        :return: True if the Player can fight, False otherwise
        """
        pass

    @abstractmethod
    def can_dig(self, token_species: str) -> bool:
        """
        Abstract method defining if the Player fulfills the requirements to dig a wall
        represented by a Token of the specified Token.species
        :param token_species: Token.species of the wall
        :return: True if the Player can dig, False otherwise
        """
        pass

    @property
    def can_retreat(self) -> bool:
        """
        Property defining if a Character can retreat after an attack
        :return: True if character can retreat after attack, False otherwise
        """
        return False

    @property
    def can_find_trap(self) -> bool:
        """
        Property defining if a Character is able to spot a trap
        :return: True if character is able to spot the trap, False otherwise
        """
        return random() < self.stats.trap_spotting_chance

    @property
    def can_disarm_trap(self) -> bool:
        """
        Property defining if a Character is able to disarm a trap
        :return: True if character is able to disarm the trap, False otherwise
        """
        return random() < self.stats.trap_disarming_chance

    def reset_objects(self) -> None:
        """
        Sets all inventory objects and special items to 0
        :return: None
        """
        for key in self.inventory.keys():
            self.inventory[key] = 0
        if self.special_items is not None:
            for key in self.special_items.keys():
                self.special_items[key] = 0

    def subtract_weapon(self) -> None:
        """
        Subtracts the weapon used
        :return: None
        """
        self.weapons -= 1

    @staticmethod
    def on_experience(player, exp_value) -> None:
        """
        Checks if the player must level up and, if so, levels up
        :param player: player instance
        :param exp_value: experience value
        :return: None
        """
        if exp_value >= player.stats.exp_to_next_level:
            start_level: int = player.player_level
            while exp_value >= player.stats.exp_to_next_level:
                exp_value -= player.stats.exp_to_next_level
                player.player_level += 1
                player.stats.exp_to_next_level = (
                    player.player_level * player.stats.base_exp_to_level_up
                )

            player.get_dungeon().game.ids.experience_bar.max = player.stats.exp_to_next_level
            player.experience = exp_value
            player.token.effect_queue = [{"level_up": False} for _ in range(player.player_level - start_level)]
            # experience bar updated by MineMadnessgame.update_interface()

    def remove_all_effects(self, turn: int = 0) -> None:
        """
        Removes all effects from the Player, regardless if they are over or not
        :param turn: turn in which all effects will be removed
        :return: None
        """
        for attribute in self.effects.keys():
            if len(self.effects[attribute]) > 0:
                for effect in self.effects[attribute]:
                    effect["end_turn"] = turn
        self.remove_effects_if_over(turn)

    def remove_effects_if_over(self, turn: int) -> None:
        """
        Removes all effects for which the effect is over
        """
        effect_names = list()

        # attributes are: "moves", "toughness", "strength"
        for attribute, effects in self.effects.items():

            for effect in effects:
                if effect["end_turn"] <= turn:
                    player_stat = getattr(self.stats, attribute)
                    if isinstance(player_stat, int):
                        player_stat -= effect["size"]
                    elif isinstance(player_stat, list):
                        player_stat[1] -= effect["size"]
                    effect_names.append(attribute)
                    setattr(self.stats, attribute, player_stat)

            self.effects[attribute] = [effect for effect in effects if effect["end_turn"] > turn]

        if self.token is not None:  # dead characters have no token
            self.token.effect_queue = self.token.effect_queue + [{effect_name: True} for effect_name in effect_names]

    def perform_passive_action(self) -> None:
        """
        Method defining the passive action that Players perform when turn is skipped (double-click on them)
        :return: None
        """
        dungeon: DungeonLayout = self.get_dungeon()
        hidden_traps_in_range: set[tuple[int,int]] = {position for position in dungeon.get_range(self.get_position(),
                                                                            self.remaining_moves)
                                                if dungeon.get_tile(position).has_token("trap")
                                                and dungeon.get_tile(position).get_token("trap").character.is_hidden}

        for position in hidden_traps_in_range:

            if dungeon.check_if_connexion(self.get_position(),
                                                     position,
                                                     [token_kind for token_kind in self.blocked_by
                                                      if token_kind != "trap"],
                                                     self.remaining_moves) and self.can_find_trap:

                trap_token = dungeon.get_tile(position).get_token("trap")
                trap_token.character.unhide()
                trap_token.show_effect_token("trap")
                self.experience += trap_token.character.stats.experience_when_found
                self.get_dungeon().game.ids.experience_bar.value = self.experience

        self.remaining_moves = 0  # one passive action per turn

    def act_on_tile(self, tile:Tile) -> None:
        """
        Handles the logic of PLayer behaviour depending on Tile.token
        :param tile: Tile upon which the Player should act
        :return: None
        """
        if tile.has_token("wall"):
            self._dig(tile)
        elif tile.has_token("monster"):
            self.fight_on_tile(tile)
        elif tile.has_token("trap"):
            if self.get_position() == tile.position:
                self.fall_in_trap(tile)
            else:
                self._disarm_trap(tile)
        else:
            if (tile.has_token("pickable") and "pickable" not in self.ignores
                    and tile.get_token("pickable").species not in self.ignores):
                self._pick_object(tile)
            if (tile.has_token("treasure") and "treasure" not in self.ignores
                    and tile.get_token("treasure").species not in self.ignores):
                self._pick_gem(tile)
            if tile.kind == "exit" and self.has_all_gems:
                self._exit_level()
                Player.check_if_all_players_out(self.game)

    def _exit_level(self) -> None:
        """
        Takes a Player out of a level
        :return: None
        """
        Player.exited.add(self.id)
        Player.in_game.remove(self.id)
        self.token.delete_token(self.token.get_current_tile())

    def _pick_object(self, tile: Tile) -> None:
        """
        Handles the logic of picking up objects
        :param tile: Tile where the object is
        :return: None
        """
        game = self.get_dungeon().game
        object_name = tile.get_token("pickable").species

        if object_name in self.special_items:
            self.special_items[object_name] += 1
            game.force_update("ability_button")

        elif object_name in self.inventory.keys():
            self.inventory[object_name] += 1
            game.inv_object = object_name

        # weapons and shovels
        else:
            character_attribute = getattr(self, f"{object_name}s")
            character_attribute += 1
            setattr(self, f"{object_name}s", character_attribute)
            game.force_update("ability_button")  # for Crusher Jane

        tile.get_token("pickable").delete_token(tile)

    def _pick_gem(self, tile:Tile)-> None:
        """
        Handles the logic of picking gems
        :param tile: Tile where the gem is
        :return: None
        """
        game = self.get_dungeon().game
        Player.gems += 1
        game.force_update("gems")
        tile.get_token("treasure").delete_token(tile)

    def fall_in_trap(self, tile:Tile) ->None:
        """
        Handles the logic of falling on traps
        :param tile: Tile where the trap is
        :return: None
        """
        tile.get_token("trap").character.show_and_damage(self)
        self.remaining_moves = 0

    def _disarm_trap(self, tile:Tile) -> None:
        """
        Handles the logic of disarming traps
        :param tile: Tile where the trap is
        :return: None
        """
        trap_token = tile.get_token("trap")
        trap_token.show_effect_token(effect="trap_out")
        self.experience += trap_token.character.stats.calculate_experience(self.get_dungeon().dungeon_level)
        self.get_dungeon().game.ids.experience_bar.value = self.experience
        trap_token.delete_token(tile)
        self.remaining_moves -= 1

    def _dig(self, wall_tile: Tile) -> None:
        """
        Handles the logic of digging
        :param wall_tile: Tile where the wall to dig is
        :return: None
        """
        if wall_tile.has_token("wall", "granite"):
            self.shovels -= 1

        if wall_tile.has_token("wall", "rock"):
            if not self.species == "hawkins":
                self.shovels -= 1

        self.remaining_moves -= self.stats.digging_moves

        wall_tile.get_token("wall").show_digging()
        wall_tile.get_token("wall").delete_token(wall_tile)

        if wall_tile.has_token("light"):
            while len(wall_tile.tokens["light"]) > 0:
                wall_tile.get_token("light").delete_token(wall_tile)
            self.get_dungeon().update_bright_spots()

    def fight_on_tile(self, opponent_tile: Tile) -> None:
        """
        Handles the logic of fighting for Players
        :param opponent_tile: Tile where the opponent is
        :return: None
        """
        opponent = opponent_tile.get_token("monster").character
        opponent = self.fight_opponent(opponent)
        self.subtract_weapon()
        self.remaining_moves -= 1

        if opponent.stats.health <= 0:
            opponent.kill_character(opponent_tile)
            self.experience += opponent.stats.experience_when_killed
            self.get_dungeon().game.ids.experience_bar.value = self.experience

    def heal(self, extra_points: int) -> None:
        """
        Handles the logic of healing
        :param extra_points: points to add to the Player.stats.health
        :return: None
        """
        self.stats.health = (
            self.stats.health + extra_points
            if self.stats.health + extra_points <= self.stats.natural_health
            else self.stats.natural_health
        )

    def kill_character(self, tile) -> None:
        """
        Kills a Player
        :param tile: Tile where the Player is
        :return: None
        """
        super().kill_character(tile)
        self.remove_all_effects()
        self.dead.append(self)

    def resurrect(self, dungeon: DungeonLayout) -> None:
        """
        Brings a dead Player back to the game
        :param dungeon: DungeonLayout were the Player should be resurrected
        :return: None
        """
        self.unbind(experience=self.on_experience)
        self.unbind(player_level=self.on_player_level)

        Player.dead.remove(self)
        self.player_level = self.player_level - 1 if self.player_level > 1 else 1
        for key, value in self.level_track[self.player_level].items():
            self.stats.__setattr__(key, value)

        # equals attributes to natural_attributes
        self.stats.__post_init__()
        self.experience = 0
        self.stats.exp_to_next_level = self.player_level * self.stats.base_exp_to_level_up
        self.reset_objects()

        location: Tile = dungeon.get_random_tile(free=True)
        location.place_item(self.kind, self.species, character=self)
        self.setup_character()

        self.bind(experience=self.on_experience)
        self.bind(player_level=self.on_player_level)

    def apply_toughness(self, damage):
        """
        Applies the Player.toughness to mitigate damage
        :param damage: damage to mitigate
        :return: mitigated damage
        """
        for effect in self.effects["toughness"]:
            effect["size"] -= damage
            if effect["size"] <= 0:
                damage = abs(effect["size"])
                self.effects["toughness"].remove(effect)
                continue
            elif effect["size"] > 0:
                damage = 0
                break
        return damage

    def check_if_overdose(self, item) -> bool:
        """
        I don't know if this will be ever used. Check if a Player consumed too many items
        :param item: item to check
        :return: True if overdosed
        """
        pass

    def _update_level_track(self, level: int) -> None:
        """
        Adds a new level to the level track
        :param level: level to add
        :return: None
        """
        self.level_track[level] = {
            "health": self.stats.natural_health,
            "moves": self.stats.natural_moves,
            "strength": self.stats.natural_strength,
        }

    def _level_up_health(self, increase: int) -> None:
        """
        Levels up Player.stats.health
        :param increase: value to increase
        :return: None
        """
        self.stats.natural_health += increase
        self.stats.health += increase

    def _level_up_moves(self, increase: int) -> None:
        """
        Levels up Player.stats.moves
        :param increase: value to increase
        :return: None
        """
        self.stats.natural_moves += increase
        self.stats.moves += increase
        self.remaining_moves += increase
        self.get_dungeon().game.activate_accessible_tiles(self.remaining_moves)

    def _level_up_strength(self, increase: tuple[int, int]) -> None:
        """
        Levels up Player.stats.strength
        :param increase: value to increase
        :return: None
        """
        self.stats.natural_strength[0] += increase[0]
        self.stats.natural_strength[1] += increase[1]
        self.stats.strength[0] += increase[0]
        self.stats.strength[1] += increase[1]

class Sawyer(Player):
    """Slow digger (takes half of initial moves each dig)
    Can pick gems
    LOW strength
    LOW health
    HIGH movement"""

    @property
    def is_hidden(self):
        return self.ability_active

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "%"
        self.name: str = "Sawyer"
        self.species: str = "sawyer"
        self.ignores: list[str] = self.ignores + ["dynamite"]

        self.stats = stats.SawyerStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] | None = {"powder": 2}
        self.ability_display: str = "Hide"
        self.ability_active: bool = False

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        """
        Determines if a Character is able to dig a certain kind of wall
        :param token_species: Token.species of the wall Token
        :return: True if can dig, False otherwise
        """
        if token_species == "rock":
            return self.shovels > 0 and self.remaining_moves >= self.stats.digging_moves
        if token_species in ["granite", "quartz"]:
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        """
        Checks if Sawyer can fight a certain monster
        :param token_species: MonsterToken.species to fight
        :return: True if the Sawyer can fight, False otherwise
        """
        return self.weapons > 0

    def on_player_level(self, instance, value):
        """Sawyer is a young, inexperienced but cunning character. Is it not particularly strong
        but her dexterity allows her to survive the most compromised situations.

        Sawyer increases 1 movement every 2 levels,
        1 health per level,
        1 recovery_end_of_level per level,
        1 max damage every 2 levels
        +0.05 in trap spotting chance every 3 levels
        """
        self._level_up_health(2)
        self.stats.recovery_end_of_level += 1

        if not value % 2 == 0:
            self._level_up_moves(1)
            self._level_up_strength((0, 1))

        if value % 3 == 0:
            self.stats.trap_spotting_chance += 0.05 \
                if self.stats.trap_spotting_chance < 1.0 else self.stats.trap_spotting_chance

        self._update_level_track(value)

    def perform_passive_action(self) -> None:
        """
        Placeholder, for the moment all passive actions are the same (finding traps) and defined within the superclass
        :return: None
        """
        super().perform_passive_action()

    def hide(self) -> None:
        """
        Hides Sawyer
        :return: None
        """
        self.special_items["powder"] -= 1
        self.ignores += ["pickable", "treasure"]
        self.token.color.a = 0.6  # changes transparency
        self.ability_active = True
        self.remaining_moves -= 1

    def unhide(self) -> None:
        """
        Reverts hiding
        :return: None
        """
        self.token.color.a = 1  # changes transparency
        self.ignores.remove("pickable")
        self.ignores.remove("treasure")
        self.ability_active = False
        self.get_dungeon().game.force_update("ability_button")  # must be here. If attacked must update button a well

    def enhance_damage(self, damage: int) -> int:
        """
        Enhances attack damage
        :param damage: damage to enhance
        :return: enhanced damage
        """
        if self.ability_active:
            damage *= self.stats.advantage_strength_incr
        return damage

class CrusherJane(Player):
    """
    Can fight with no weapons (MEDIUM strength)
    Stronger if fight with weapons  (HIGH strength)
    Cannot pick gems
    LOW movement
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "&"
        self.name: str = "Crusher Jane"
        self.species: str = "crusherjane"
        self.ignores: list[str] = self.ignores + ["powder", "dynamite", "treasure"]

        self.stats = stats.CrusherJaneStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] = {"weapons": self.weapons}
        self.ability_display: str = "Weapons"
        self.ability_active: bool = False

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        """
        Checks if CrusherJane can dig
        :param token_species: WallToken species to dig
        :return: True if can dig, False otherwise
        """
        if token_species == "rock":
            return self.shovels > 0 and self.remaining_moves >= self.stats.digging_moves
        if token_species in ["granite", "quartz"]:
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        """
        Crusher Jane can always fight
        :param token_species: MonsterToken.species to fight
        :return: True, always
        """
        return True

    def on_player_level(self, instance, value):
        """Crusher Jane is a big, strong and not particularly intelligent woman. Relies on brute strength and on her
        physical endurance to resist the most brutal hits.
        Crusher Jane increases 1 movement every 4 levels,
        2 health every level,
        (+1, +2) strength per level,
        1 recovery_end_of_level per level
        """
        self._level_up_health(3)
        self._level_up_strength((1, 2))
        if not value % 2 == 0:
            self.stats.recovery_end_of_level += 1
        if value % 4 == 0:
            self._level_up_moves(1)
        self._update_level_track(value)

    def perform_passive_action(self) -> None:
        """
        Placeholder, for the moment all passive actions are the same (finding traps) and defined within the superclass
        :return: None
        """
        super().perform_passive_action()

    def enhance_damage(self, damage: int) -> int:
        """
        Enhances attack damage
        :param damage: damage to enhance
        :return: enhanced damage
        """
        if self.ability_active:
            damage *= self.stats.advantage_strength_incr
        return damage

    def subtract_weapon(self) -> None:
        """
        Manages what happens with the ability button when the weapon is substracted
        :return: None
        """
        if self.ability_active:
            super().subtract_weapon()
            if self.weapons == 0:
                game = self.get_dungeon().game
                self.ability_active = False
                game.force_update("ability_button")

class Hawkins(Player):
    """Can dig without shovels
    Does not pick shovels
    Can fight with weapons
    Cannot pick gems
    LOW health
    MEDIUM strength
    MEDIUM movement"""

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "?"
        self.name: str = "Hawkins"
        self.species: str = "hawkins"
        self.ignores: list[str] = self.ignores+ ["powder", "treasure"]

        self.stats = stats.HawkinsStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] | None = {"dynamite": 2}
        self.ability_display: str = "Dynamite"
        self.ability_active: bool = False

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        """
        Checks if Hawkins can dig
        :param token_species: wall to dig
        :return: True if can dig, False otherwise
        """
        if token_species == "rock":
            return True
        if token_species == "granite":
            return self.shovels > 0 and self.remaining_moves >= self.stats.digging_moves
        if token_species == "quartz":
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        """
        Checks if Hawkins can fight
        :param token_species: MonsterToken.species to fight
        :return: True if Hawkins can fight, False otherwise
        """
        return self.weapons > 0

    def on_player_level(self, instance, value):
        """Hawkins is an old and wise man. It is trained by the most difficult situations of life, and it is strong
        for his age. But his most valuable asset is his wits.
        Hawkins increases 1 movement every 3 levels
        1 health point every level
        1 recovery_end_of_level every 3 levels
        1 max damage every level and 1 min damage every 2 levels
        + 0.05 in trap_spotting every 2 levels
        """
        self._level_up_health(2)
        self._level_up_strength((0, 1))
        if not value % 2 == 0:
            self._level_up_strength((1, 0))
        if value % 3 == 0:
            self._level_up_moves(1)
            self.stats.recovery_end_of_level += 1
        if value % 2 == 0:
            self.stats.trap_spotting_chance += 0.05 \
                if self.stats.trap_spotting_chance < 1.0 else self.stats.trap_spotting_chance
        self._update_level_track(value)

    def perform_passive_action(self) -> None:
        """
        Placeholder, for the moment all passive actions are the same (finding traps) and defined within the superclass
        :return: None
        """
        super().perform_passive_action()

    @property
    def using_dynamite(self):
        """
        Checks if Hawkins is using dynamite
        :return: True if using, False otherwise
        """
        return self.ability_active

    def throw_dynamite(self, tile: Tile) -> None:
        """
        Throws dynamite
        :param tile: Tile where dynamite lands
        :return: None
        """
        self.special_items["dynamite"] -= 1
        self.ability_active = False
        self.token.dungeon.game.force_update("ability_button")
        tile.dynamite_fall()
        self.remaining_moves -= 1

    def enhance_damage(self, damage: int) -> int:
        """
        Placeholder. Hawkins cannot enhance damage
        :param damage: damage to enhance
        :return: same damage
        """
        return damage

