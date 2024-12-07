from __future__ import annotations
from abc import ABC, abstractmethod
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

from character_class import Character
import game_stats as stats


class Player(Character, ABC, EventDispatcher):

    experience = NumericProperty(0)
    player_level = NumericProperty(1)

    # this is the starting order as defined by Player.set_starting_player_order()
    player_chars: tuple[str,str,str] = ("%", "?", "&")  # % sawyer, ? hawkins, & crusher jane
    data: list[Character] = list()
    dead_data: list[Character] = list()
    exited: set[Character] = set()
    gems: int = 0

    @classmethod
    def clear_character_data(cls) -> None:
        """
        Removes all characters from the Player.data, Player.dead_data and Player.exited list and resets class attributes
        :return: None
        """
        super().clear_character_data()
        cls.dead_data.clear()
        cls.exited.clear()

    @classmethod
    def set_starting_player_order(cls) -> None:
        """
        Sets the starting player turn order: Sawyer, Hawkins, Crusher Jane
        :return: None
        """
        sawyer = next((player for player in cls.data if isinstance(player, Sawyer)), None)
        hawkins = next((player for player in cls.data if isinstance(player, Hawkins)), None)
        crusherjane = next((player for player in cls.data if isinstance(player, CrusherJane)), None)
        cls.data = [item for item in [sawyer, hawkins, crusherjane] if item is not None]
        cls.rearrange_ids()

    @classmethod
    def swap_characters(cls, index_char_1: int, index_char_2: int) -> None:
        """
        Swaps the order of 2 characters in cls.data
        :param index_char_1: index of a character
        :param index_char_2: index of another character
        :return: None
        """
        cls.data[index_char_2], cls.data[index_char_1] = cls.data[index_char_1], cls.data[index_char_2]
        cls.rearrange_ids()

    @classmethod
    def all_players_alive(cls):
        return len(cls.data) == len(cls.player_chars)

    @classmethod
    def all_players_dead(cls):
        return len(cls.dead_data) == len(cls.player_chars)

    @classmethod
    def check_if_dead(cls, player_species):
        return any(player.species == player_species for player in cls.dead_data)

    @classmethod
    def get_alive_players(cls) -> set[str] | tuple[str:str:str]:
        """
        Determines the number of alive players at the end of a level
        :return: set or tuple containing the characters representing live players
        """
        if cls.all_alive():
            return cls.player_chars
            # return "&"
        else:
            return {player.char for player in cls.exited}

    @classmethod
    def transfer_player(cls, species: str) -> Player:
        """
        Retrieves players from Players.exited or Players.data to transfer them to a dungeon level
        :param species: Player.species of the player to be retrieved
        :return: the Player instance
        """
        if len(cls.exited) > 0:
            for player in cls.exited:
                if player.species == species:
                    player.heal(player.stats.recovery_end_of_level)
                    player.ability_active = False
                    return player
        elif len(cls.data) > 0:
            for player in cls.data:
                if player.species == species:
                    return player

    @classmethod
    def all_alive(cls) -> bool:
        """
        Checks if all instances of the class (players or monsters) dead or out of game
        """
        return len(cls.dead_data) == 0


    def __init__(self):
        super().__init__()
        self.kind: str = "player"
        self.blocked_by: list[str] = ["wall", "monster"]
        self.cannot_share_tile_with: list[str] = ["wall", "monster", "player"]
        self.ignores: list[str] = ["light"]
        self.step_transition: str = "in_out_quad" # walking
        self.step_duration: float = 0.35

        # attributes exclusive of Player class
        self.inventory: dict[str:int] = {
            "jerky": 2,
            "coffee": 0,
            "tobacco": 0,
            "whisky": 0,
            "talisman": 0,
        }
        self.effects: dict[str:list] = {"moves": [], "toughness": [], "strength": []}
        self.state: str | None = None
        self.special_items: dict[str:int] | None = None
        self.level_track: dict[int:dict] = dict()

        self.bind(experience=self.on_experience)
        self.bind(player_level=self.on_player_level)


    @abstractmethod
    def on_player_level(self, instance, value):
        pass

    @abstractmethod
    def enhance_damage(self, damage: int) -> int:
        pass

    @abstractmethod
    def unhide(self) -> None:
        pass


    @property
    def has_all_gems(self) -> bool:
        return Player.gems == self.get_dungeon().game.total_gems

    def has_item(self, item: str) -> bool:
        return self.inventory[item] > 0

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
        game=self.get_dungeon().game
        self.stats.weapons -= 1
        game.update_switch("weapons")

    def on_experience(self, instance, value):

        if value >= self.stats.exp_to_next_level:
            self.player_level += 1
            self.stats.exp_to_next_level = (
                self.player_level * self.stats.base_exp_to_level_up
            )
            self.experience = 0
            self.token.show_effect_token(
                "level_up",
                self.token.shape.pos,
                self.token.shape.size,
            )
            # experience bar updated by Cragpeongame.update_interface()

    def remove_all_effects(self, turn: int = 0) -> None:
        """
        Removes all effects from the Player, regardless if they are over or not
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
        attribute_names = list()

        # attributes are: "moves", "toughness", "strength"
        for attribute, effects in self.effects.items():

            for effect in effects:
                if effect["end_turn"] <= turn:
                    player_stat = getattr(self.stats, attribute)
                    if isinstance(player_stat, int):
                        player_stat -= effect["size"]
                    elif isinstance(player_stat, list):
                        player_stat[1] -= effect["size"]
                    effects.remove(effect)
                    attribute_names.append(attribute)
                    setattr(self.stats, attribute, player_stat)
                    continue

        self.token.modified_attributes = attribute_names

    def act_on_tile(self, tile:Tile) -> None:
        """
        Handles the logic of PLayer behaviour depending on Tile.token
        :param tile: Tile upon which the Player should behave
        :return: None
        """
        if tile.has_token("wall"):
            self._dig(tile)
            self.token.dungeon.game.update_switch("character_done")
        elif tile.has_token("monster"):
            self.fight_on_tile(tile)
            self.token.dungeon.game.update_switch("character_done")
        else:
            if tile.has_token("pickable"):
                self._pick_object(tile)
            if tile.has_token("treasure"):
                self._pick_treasure(tile)
            if tile.kind == "exit" and self.has_all_gems:
                self._exit_level()
                tile.dungeon.game.update_switch("player_exited")
            else:
                self.token.dungeon.game.update_switch("character_done")

    def _exit_level(self) -> None:
        Player.exited.add(self)
        Player.data.remove(self)
        self.rearrange_ids()
        self.token.delete_token(self.token.get_current_tile())

    def _pick_object(self, tile: Tile) -> None:

        game = self.get_dungeon().game
        object_name = tile.get_token("pickable").species

        if object_name not in self.ignores:
            if object_name in self.special_items:
                self.special_items[object_name] += 1
                game.update_switch("ability_button")

            elif object_name in self.inventory.keys():
                self.inventory[object_name] += 1
                game.inv_object = object_name

            else:
                # do not use f-strings here or Buildozer will crash
                character_attribute = getattr(self.stats, f"{object_name}s")
                character_attribute += 1
                setattr(self.stats, f"{object_name}s", character_attribute)
                game.update_switch(f"{object_name}s")
                game.update_switch("ability_button")  # for Crusher Jane

            tile.get_token("pickable").delete_token(tile)

    def _pick_treasure(self, tile:Tile)-> None:
        game=self.get_dungeon().game
        if "treasure" not in self.ignores:
            Player.gems += 1
            game.update_switch("gems")
            tile.get_token("treasure").delete_token(tile)

    def _dig(self, wall_tile: Tile) -> None:

        game = self.get_dungeon().game

        if wall_tile.has_token("wall", "granite"):
            self.stats.shovels -= 1
            game.update_switch("shovels")

        if wall_tile.has_token("wall", "rock"):
            if not isinstance(self, Hawkins):
                self.stats.shovels -= 1
                game.update_switch("shovels")
        self.stats.remaining_moves -= self.stats.digging_moves
        wall_tile.get_token("wall").show_digging()
        wall_tile.get_token("wall").delete_token(wall_tile)

    def fight_on_tile(self, opponent_tile) -> None:
        opponent = opponent_tile.get_token("monster").character
        opponent = self.fight_opponent(opponent)
        self.subtract_weapon()

        if opponent.stats.health <= 0:
            self.experience += opponent.stats.experience_when_killed
            self.token.dungeon.game.ids.experience_bar.value = self.experience
            opponent.kill_character(opponent_tile)


    def heal(self, extra_points: int):
        self.stats.health = (
            self.stats.health + extra_points
            if self.stats.health + extra_points <= self.stats.natural_health
            else self.stats.natural_health
        )

    def kill_character(self, tile):
        super().kill_character(tile)
        self.dead_data.append(self)

    def resurrect(self, dungeon: DungeonLayout) -> None:
        """
        Brings a dead Player back to the game
        :param dungeon: DungeonLayout were the Player should be resurrected
        :return: None
        """
        self.unbind(experience=self.on_experience)
        self.unbind(player_level=self.on_player_level)

        Player.dead_data.remove(self)
        self.player_level = self.player_level - 3 if self.player_level > 3 else 1
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

        #print("RESURRECTED")
        #print(self.player_level)
        #print(self.stats)

    def apply_toughness(self, damage):

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

    def check_if_overdose(self, item):
        pass

    def _update_level_track(self, level: int) -> None:

        self.level_track[level] = {
            "health": self.stats.natural_health,
            "moves": self.stats.natural_moves,
            "strength": self.stats.natural_strength,
        }

    def _level_up_health(self, increase: int) -> None:

        self.stats.natural_health += increase
        self.stats.health += increase

    def _level_up_moves(self, increase: int) -> None:

        self.stats.natural_moves += increase
        self.stats.moves += increase
        self.stats.remaining_moves += increase
        self.get_dungeon().game.activate_accessible_tiles(self.stats.remaining_moves)

    def _level_up_strength(self, increase: tuple[int, int]) -> None:

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

        self.special_items: dict[str:int] | None = {"powder": 5}
        self.ability_display: str = "Hide"
        self.ability_active: bool = False

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        if token_species == "rock":
            return self.stats.shovels > 0 and self.stats.remaining_moves >= self.stats.digging_moves
        if token_species in ["granite", "quartz"]:
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        return self.stats.weapons > 0

    def on_player_level(self, instance, value):
        """Sawyer is a young, inexperienced but cunning character. Is it not particularly strong
        but her dexterity allows her to survive the most compromised situations.

        Sawyer increases 1 movement every 2 levels,
        1 health per level,
        1 recovery_end_of_level per level,
        1 advantage_strength_increase per level
        1 max damage every 2 levels"""

        self._level_up_health(1)
        self.stats.advantage_strength_incr += 1
        self.stats.recovery_end_of_level += 1

        if not value % 2 == 0:
            self._level_up_moves(1)
            self._level_up_strength((0, 1))

        self._update_level_track(value)

        #print("SAWYER NEW LEVEL")
        #print(value)
        #print(self.level_track)
        #print(self.stats)

    def hide(self):
        self.token.color.a = 0.6  # changes transparency
        self.ignores += ["pickable","treasure"]

    def unhide(self):
        game=self.get_dungeon().game
        self.token.color.a = 1  # changes transparency
        self.ignores.remove("pickable")
        self.ignores.remove("treasure")
        self.ability_active = False
        game.update_switch("ability_button")
        game.update_switch("character_done")

    def enhance_damage(self, damage) -> int:
        if self.ability_active:
            damage += self.stats.advantage_strength_incr
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

        self.special_items: dict[str:int] = {"weapons": self.stats.weapons}
        self.ability_display: str = "Use Weapons"
        self.ability_active: bool = False

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        if token_species == "rock":
            return self.stats.shovels > 0 and self.stats.remaining_moves >= self.stats.digging_moves
        if token_species in ["granite", "quartz"]:
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        return True

    def on_player_level(self, instance, value):
        """Crusher Jane is a big, strong and not particularly intelligent woman. Relies on brute strength and on her
        physical endurance to resist the most brutal hits.
        Crusher Jane increases 1 movement every 4 levels,
        2 health every level,
        (+1, +2) strength per level,
        1 recovery_end_of_level per level
        1 adv. strength every 2 levels.
        """
        self._level_up_health(2)
        self._level_up_strength((1, 2))

        if not value % 2 == 0:
            self.stats.recovery_end_of_level += 1
            self.stats.advantage_strength_incr += 1

        if value % 4 == 0:
            self._level_up_moves(1)

        self._update_level_track(value)

        #print("CRUSHER JANE NEW LEVEL")
        #print(value)
        #print(self.level_track)
        #print(self.stats)

    def enhance_damage(self, damage: int) -> int:
        if self.ability_active:
            damage += self.stats.advantage_strength_incr
        return damage

    def unhide(self) -> None:
        pass

    def subtract_weapon(self) -> None:

        if self.ability_active:
            super().subtract_weapon()
            if self.stats.weapons == 0:
                game = self.get_dungeon().game
                self.ability_active = False
                game.update_switch("ability_button")

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
        self.ignores: list[str] = self.ignores+ ["gem", "powder", "treasure"]

        self.stats = stats.HawkinsStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] | None = {"dynamite": 2}
        self.ability_display: str = "Use Dynamite"
        self.ability_active: bool = False

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        if token_species == "rock":
            return True
        if token_species == "granite":
            return self.stats.shovels > 0 and self.stats.remaining_moves >= self.stats.digging_moves
        if token_species == "quartz":
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        return self.stats.weapons > 0

    def on_player_level(self, instance, value):
        """Hawkins is an old and wise man. It is trained by the most difficult situations of life, and it is strong
        for his age. But his most valuable asset is his wits.
        Hawkins increases 1 movement every 3 levels
        1 health point every level
        1 recovery_end_of_level every 3 levels
        1 max damage every level and 1 min damage every 2 levels
        """
        self._level_up_health(1)
        self._level_up_strength((0, 1))

        if not value % 2 == 0:
            self._level_up_strength((1, 0))

        if value % 3 == 0:
            self._level_up_moves(1)
            self.stats.recovery_end_of_level += 1

        self._update_level_track(value)

        #print("HAWKINS NEW LEVEL")
        #print(value)
        #print(self.level_track)
        #print(self.stats)

    @property
    def using_dynamite(self):
        return self.ability_active


    def throw_dynamite(self, tile: Tile):
        self.special_items["dynamite"] -= 1
        self.stats.remaining_moves -= 1
        self.ability_active = False
        self.token.dungeon.game.update_switch("ability_button")
        tile.dynamite_fall()
        self.token.dungeon.game.update_switch("character_done")

    def enhance_damage(self, damage: int) -> int:
        return damage

    def unhide(self) -> None:
        pass

