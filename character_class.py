from __future__ import annotations
from random import randint
from abc import ABC, abstractmethod

from kivy.event import EventDispatcher
from kivy.properties import NumericProperty


class Character(ABC, EventDispatcher):

    data: list[Character] | None = None
    remaining_moves = NumericProperty(None)

    @classmethod
    def clear_character_data(cls) -> None:
        """
        Removes all characters from the Character.data list
        :return: None
        """
        cls.data.clear()

    @classmethod
    def rearrange_ids(cls) -> None:
        """
        Rearranges characters ids to match their order in Character.data list
        :return: None
        """
        for character in cls.data:
            character.id = cls.data.index(character)

    @classmethod
    def initialize_moves_attacks(cls) -> None:
        """
        Resets remaining moves of all characters of the class back to the maximum
        :return: None
        """
        for character in cls.data:
            character.remaining_moves = character.stats.moves

    @classmethod
    def all_dead_or_out(cls) -> bool:
        """
        Checks if all instances characters of the class are dead or out of game
        :return:: True if all are dead or out of game, False otherwise
        """
        return len(cls.data) == 0


    def __init__(self, **kwargs):

        """
        Those are common attributes to all characters (Players and Monsters).
        Initialized to corresponding type when instantiating Player or Monster, except
        id, position, token and dungeon, initialized in DungeonLayout.place_item()
        Exclusive attributes of each class are added within corresponding classes.
        """
        super().__init__(**kwargs)
        self.char: str | None = None
        self.name: str | None = None
        self.id: int | None = None   # initialized in DungeonLayout.place_item()
        self.kind: str | None = None
        self.species: str | None = None
        self.token: Token | None = None  # initialized in DungeonLayout.place_item()
        self.stats: CharacterStats | None = None
        self.blocked_by: list | None = None
        self.cannot_share_tile_with: list | None = None
        self.ignores: list | None = None
        self.invisible: bool | None = None
        self.step_transition: str | None = None  # defines kind of movement (walk, stomp, glide...)
        self.step_duration: float | None = None  # defines speed of movement, from 0 to 1
        self.inventory: dict[str:int] | None = None  # needed for MineMadnessGame_on_inv_object()

    def on_remaining_moves(self, character: Character, value: int) -> None:
        """
        Notifies the game when the character moves
        :return: None
        """
        if character.has_moved:
            self.get_dungeon().game.character_moved()

    def to_dict(self):
        """
        Converts the instance of the class to a dictionary containing its attributes and their values
        :return: dictionary containing the names of the attributes as keys and the values as values
        """
        # Token objects are not JSON serializable. They ara added within DungeonLayout.match_blueprint()
        as_dict = {key: value for key,value in vars(self).items() if key != "token"}
        as_dict["stats"] = self.stats.to_dict()
        return as_dict

    def overwrite_attributes(self, attributes_dict: dict) -> None:
        """
        Overwrites the default attributes of the Character with custom ones
        :param attributes_dict: dictionary containing the names of the attributes as keys and the new values
        as values
        :return: None
        """
        for attribute, value in attributes_dict.items():
            if attribute == "stats":
                self.stats.overwrite_attributes(attributes_dict["stats"])
            else:
                setattr(self, attribute, value)


    def setup_character(self):
        """
        Sets up the character when its CharacterToken is placed onto the tile
        :return: None
        """
        self.id = len(self.__class__.data)
        self.__class__.data.append(self)

    def get_position(self) -> tuple[int,int]:
        """
        Returns the position of the Character.token
        :return: coordinates of the position of the Character.token
        """
        return self.token.position

    def get_dungeon(self) -> DungeonLayout:
        """
        Returns the dungeon where the Character.token is
        :return: DungeonLayout of the dungeon
        """
        return self.token.dungeon

    @abstractmethod
    def has_all_gems(self) -> bool:
        """
        Defines if the all the characters of the team (Players or Monsters) have all gems collected
        :return: bool
        """
        pass

    @abstractmethod
    def act_on_tile(self, tile: Tile) -> None:
        """
        Abstract method defining the behavior of a character when landing on a new tile
        :param tile: tile where character lands
        :return: None
        """
        pass

    @abstractmethod
    def can_fight(self, token_species: str) -> bool:
        """
        Abstract method defining if the character fulfills the requirements to fight with an opponent
        represented by a Token of the specified Token.species
        :param token_species: Token.species of the opponent
        :return: True if the character can fight, False otherwise
        """
        pass

    @abstractmethod
    def can_dig(self, token_species: str) -> bool:
        """
        Abstract method defining if the character fulfills the requirements to dig a wall
        represented by a Token of the specified Token.species
        :param token_species: Token.species of the wall
        :return: True if the character can dig, False otherwise
        """
        pass

    @abstractmethod
    def can_retreat(self) -> bool:
        """
        Property defining if a Character can retreat after an attack
        :return: True if character can retreat after attack, False otherwise
        """
        pass

    @property
    def is_hidden(self) -> bool:
        """
        Checks if the character is hidden
        :return: True if character is hidden, False otherwise
        """
        return False

    @property
    def is_exited(self) -> bool:  # needed for everybody for self.fight_on_tile()
        """
        Checks if the character has exited the level
        :return: True if character is hidden, False otherwise
        """
        return False

    @property
    def using_dynamite(self) -> bool:  # needed for everybody for Token.on_slide_completed()
        """
        Checks if the character is using dynamite
        :return: True if character is using dynamite, False otherwise
        """
        return False

    @property
    def has_moves_left(self) -> bool:
        """
        Checks if has moves left
        :return: True if character has moves left, False otherwise
        """
        return self.remaining_moves > 0

    @property
    def has_moved(self) -> bool:
        """
        Checks if the character has moved this turn
        :return: True if character has moved, False otherwise
        """
        return self.remaining_moves < self.stats.moves

    def hide(self) -> None:
        """
        Placeholder
        """
        pass

    def unhide(self) -> None:
        """
        Placeholder, needed for Monster.fight_on_tile()
        """
        pass

    def enhance_damage(self, damage: int) -> int:
        """
        Placeholder, needed for Monster.fight_on_tile()
        :return:: enhanced damage (if applicable)
        """
        return damage

    def apply_toughness(self, damage: int) -> int:  # needed for everybody for self.fight_on_tile()
        """
        Placeholder, needed for Monster.fight_on_tile()
        :return: reduced damage
        """
        return damage

    def fight_opponent(self, opponent: Character) -> Character:
        """
        Generic fighting method. See Player class for particularities in players
        :param opponent: opponent Character
        :return: opponent Character with inflicted damage
        """
        damage = randint(self.stats.strength[0], self.stats.strength[1])
        damage = opponent.apply_toughness(damage)
        damage = self.enhance_damage(damage)

        if self.is_hidden:
            self.unhide()
        if opponent.is_hidden:
            opponent.unhide()

        opponent.stats.health -= damage
        opponent.token.show_damage()

        return opponent


    def kill_character(self, tile: Tile) -> None:
        """
        Removes the character from the game
        :param tile:: tile in which the character to kill is located
        :return: None
        """
        del self.__class__.data[self.id]
        self.__class__.rearrange_ids()
        self.token.delete_token(tile)
