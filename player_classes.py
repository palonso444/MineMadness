from __future__ import annotations
from abc import ABC, abstractmethod
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

from character_class import Character
from crapgeon_utils import check_if_multiple, tuple_remove
import game_stats as stats


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
    def swap_characters(cls, index_char_1, index_char_2):
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
    def transfer_player(cls, name: str) -> Character:
        """
        Heals and disables the ability of exited players and transfers them to the next level.
        """

        for player in cls.exited:
            if player.name == name:
                player.heal(player.stats.recovery_end_of_level)
                player.ability_active = False
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
        self.blocked_by: tuple = ("wall", "monster")
        self.cannot_share_tile_with: tuple = ("wall", "monster", "player")
        self.ignores: tuple = (None,)

        # attributes exclusive of Player class
        self.inventory: dict[str:int] = {
            "jerky": 2,
            "coffee": 0,
            "tobacco": 0,
            "whisky": 2,
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

    @abstractmethod
    def subtract_weapon(self) -> None:
        """
        Subtracts used weapons in combat (if applicable)
        """
        pass

    @property
    def has_all_gems(self):
        return Player.gems == self.dungeon.game.total_gems

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


    def on_experience(self, instance, value):

        if value >= self.stats.exp_to_next_level:
            self.player_level += 1
            self.stats.exp_to_next_level = (
                self.player_level * self.stats.base_exp_to_level_up
            )
            self.experience = 0
            self.dungeon.show_effect_token(
                "talisman_level_up",
                self.token.shape.pos,
                self.token.shape.size,
            )
            # experience bar updated by Cragpeongame.update_interface()
            print("UPDATEEE")

            print("TO NEXT LEVEL")
            print(self.stats.exp_to_next_level)

    def remove_effects(self, turn: int) -> None:
        """
        Removes all effects for which the effect is over
        """
        attribute_names = list()

        # attributes are: "moves", "toughness", "strength"
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

        self.token.modified_attributes = attribute_names


    def act_on_tile(self, tile:Tile) -> None:

        if tile.has_token("player"):
            if tile.get_token("player").character == self:
                #this causes a bug
                #tile.get_token("player").character.stats.remaining_moves = 0
                tile.get_token("player").path = None
            else:
                self.token.dungeon.game.switch_character(tile.get_token("player").character)

        if tile.kind == "exit" and self.has_all_gems:
            self.exit_level()
            self.token.dungeon.game.update_switch("player_exited")
        else:
            if self.using_dynamite:
                self.throw_dynamite()
                self.token.dungeon.game.update_switch("ability_button")
                if tile.has_token("monster"):
                    tile.get_token("monster").token_dodge()
                else:
                    tile.dynamite_fall()

            elif tile.has_token("player") and tile.get_token("player").character == self:
                tile.get_token("player").character.stats.remaining_moves = 0
                tile.get_token("player").path = None

            elif tile.has_token("pickable"):
                self.pick_object(tile)
            elif tile.has_token("treasure"):
                self.pick_treasure(tile)

            elif tile.has_token("wall"):
                self.dig(tile)

            elif tile.has_token("monster"):
                self.fight_on_tile(tile)

            self.token.dungeon.game.update_switch("character_done")

    def exit_level(self) -> None:
        Player.exited.add(self)
        self.rearrange_ids()
        self.token.delete_token(self.token.get_current_tile())

    def pick_object(self, tile: Tile) -> None:

        game = self.dungeon.game
        # if tile.token.species not in self.ignores:
        if "pickable" not in self.ignores:
            if tile.tokens["pickable"].species in self.special_items:
                self.special_items[tile.token.species] += 1
                game.update_switch("ability_button")

            elif tile.tokens["pickable"].species in self.inventory.keys():
                self.inventory[tile.tokens["pickable"].species] += 1
                game.inv_object = tile.tokens["pickable"].species

            else:
                character_attribute = getattr(self.stats, tile.token.species + "s")
                character_attribute += 1
                setattr(self.stats, tile.token.species + "s", character_attribute)
                game.update_switch(tile.token.species + "s")
                game.update_switch("ability_button")  # for Crusher Jane

            tile.tokens["pickable"].delete_token(tile)

    def pick_treasure(self, tile:Tile)-> None:
        game=self.dungeon.game
        if "treasure" not in self.ignores:
            Player.gems += 1
            game.update_switch("gems")
            tile.tokens["treasure"].delete_token(tile)

    def dig(self, wall_tile: Tile) -> None:

        game = self.dungeon.game

        if self.stats.shovels > 0:
            if "digging" not in self.free_actions or wall_tile.has_token("wall", "granite"):
                self.stats.shovels -= 1
                game.update_switch("shovels")
        self.stats.remaining_moves -= self.stats.digging_moves

        wall_tile.tokens["wall"].show_digging()
        wall_tile.tokens["wall"].delete_token(wall_tile)

        # if digging a wall recently created by dynamite
        if wall_tile.dodging_finished:
            wall_tile.dodging_finished = False

    def fight_on_tile(self, opponent_tile) -> None:
        opponent = opponent_tile.tokens["monster"].character
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

    def apply_toughness(self, damage):

        i = 0
        while i < len(self.effects["toughness"]):
            self.effects["toughness"][i]["size"] -= damage

            if self.effects["toughness"][i]["size"] <= 0:
                damage = abs(self.effects["toughness"][i]["size"])
                self.effects["toughness"].remove(self.effects["toughness"][i])
                continue

            elif self.effects["toughness"][i]["size"] > 0:
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
        self.dungeon.game.activate_accessible_tiles()

    def _level_up_strength(self, increase: tuple[int]) -> None:

        self.stats.natural_strength = (
            self.stats.natural_strength[0] + increase[0],
            self.stats.natural_strength[1] + increase[1],
        )
        self.stats.strength = (
            self.stats.strength[0] + increase[0],
            self.stats.strength[1] + increase[1],
        )

class Sawyer(Player):
    """Slow digger (takes half of initial moves each dig)
    Can pick gems
    LOW strength
    LOW health
    HIGH movement"""

    @property
    def is_hidden(self):
        return self.ability_active

    def __init__(self):
        super().__init__()
        self.char: str = "%"
        self.name: str = "Sawyer"
        self.ignores = ("dynamite",)

        self.stats = stats.SawyerStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] | None = {"powder": 2}
        self.ability_display: str = "Hide"
        self.ability_active: bool = False

    def can_dig(self, token_species: str) -> bool:
        if token_species == "rock":
            return self.stats.shovels > 0 and self.stats.remaining_moves >= self.stats.digging_moves
        if token_species in ["granite", "quartz"]:
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        return self.stats.weapons > 0

    def on_player_level(self, instance, value):
        """Sawyer is a young, inexperienced but dexterous character. Is it not particularly strong
        but has a lot of cunning that allows her to survive compromised situations.

        Sawyer increases 1 movement every 2 levels,
        1 health per level,
        1 recovery_end_of_level per level,
        1 advantage_strength_increase per level
        1 max damage every 2 levels"""

        self._level_up_health(1)
        self.stats.advantage_strength_incr += 1
        self.stats.recovery_end_of_level += 1

        if not check_if_multiple(value, 2):
            self._level_up_moves(1)
            self._level_up_strength((0, 1))

        self._update_level_track(value)

        print(self.level_track)
        print(self.stats)

    def hide(self):
        self.token.color.a = 0.6  # changes transparency
        self.ignores += ("pickable",)

    def unhide(self):
        game=self.dungeon.game
        self.token.color.a = 1  # changes transparency
        self.ignores = tuple_remove(self.ignores, "pickable")
        self.ability_active = False
        game.update_switch("ability_button")

    def enhance_damage(self, damage) -> int:
        if self.ability_active:
            damage += self.stats.advantage_strength_incr
        return damage

    def subtract_weapon(self):
        game=self.token.dungeon.game
        self.stats.weapons -= 1
        game.update_switch("weapons")

class CrusherJane(Player):
    """
    Can fight with no weapons (MEDIUM strength)
    Stronger if fight with weapons  (HIGH strength)
    Cannot pick gems
    LOW movement
    """

    def __init__(self):
        super().__init__()
        self.char: str = "&"
        self.name: str = "Crusher Jane"
        self.ignores: tuple = ("gem", "powder", "dynamite")

        self.stats = stats.CrusherJaneStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] = {"weapons": self.stats.weapons}
        self.ability_display: str = "Use Weapons"
        self.ability_active: bool = False

    def can_dig(self, token_species: str) -> bool:
        if token_species == "rock":
            return self.stats.shovels > 0 and self.stats.remaining_moves >= self.stats.digging_moves
        if token_species in ["granite", "quartz"]:
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        return True

    def on_player_level(self, instance, value):
        """Crusher Jane is a big, strong and not particularly intelligent women. Relies on brute strength and on her
        physical endurance to resist the most brutal hits.
        Crusher Jane increases 1 movement every 4 levels,
        2 health every level,
        (+1, +2) strength per level,
        1 recovery_end_of_level per level
        1 adv. strength every 2 levels.
        """

        print("CRUSHER JANE LEVEL UP!")
        print(value)

        self._level_up_health(2)
        self._level_up_strength((1, 2))

        if not check_if_multiple(value, 2):
            self.stats.recovery_end_of_level += 1
            self.stats.advantage_strength_incr += 1

        if check_if_multiple(value, 4):
            self._level_up_moves(1)

        self._update_level_track(value)

        print(self.level_track)

        print(self.stats)

    def enhance_damage(self, damage: int) -> int:
        if self.ability_active:
            damage += self.stats.advantage_strength_incr
        return damage

    def unhide(self) -> None:
        pass

    def subtract_weapon(self) -> None:

        if self.ability_active:
            game = self.dungeon.game
            self.stats.weapons -= 1
            game.update_switch("weapons")
            if self.stats.weapons == 0:
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

    def __init__(self):
        super().__init__()
        self.char: str = "?"
        self.name: str = "Hawkins"
        self.ignores: tuple = ("gem", "powder")

        self.stats = stats.HawkinsStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] | None = {"dynamite": 2}
        self.ability_display: str = "Use Dynamite"
        self.ability_active: bool = False

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
        """Hawkins is an old and wise man. It is trained by the most difficult situations of life and it is strong
        for his age. But his most valuable asset is his wits.
        Hawkins increases 1 movement every 3 levels
        1 health point every level
        1 recovery_end_of_level every 3 levels
        1 max damage every level and 1 min damage every 2 levels"""

        print("HAWKINS LEVEL UP!")
        print(value)

        self._level_up_health(1)
        self._level_up_strength((0, 1))

        if not check_if_multiple(value, 2):
            self._level_up_strength((1, 0))

        if check_if_multiple(value, 3):
            self._level_up_moves(1)
            self.stats.recovery_end_of_level += 1

        self._update_level_track(value)

        print(self.level_track)
        print(self.stats)

    @property
    def using_dynamite(self):
        return self.ability_active

    def throw_dynamite(self):
        self.special_items["dynamite"] -= 1
        self.stats.remaining_moves -= 1
        self.ability_active = False

    def enhance_damage(self, damage: int) -> int:
        return damage

    def unhide(self) -> None:
        pass

    def subtract_weapon(self) -> None:
        game=self.dungeon.game
        self.stats.weapons -= 1
        game.update_switch("weapons")
