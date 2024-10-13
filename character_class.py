from __future__ import annotations
from random import randint
from abc import ABC, abstractmethod


class Character(ABC):

    data: list[Character] | None = None

    @classmethod
    def rearrange_ids(cls) -> None:
        """
        Rearranges characters ids to match their order in Character.data list
        :return: None
        """
        for character in cls.data:
            character.id = cls.data.index(character)

    @classmethod
    def reset_moves(cls) -> None:
        """
        Resets remaining moves of all characters of the class back to the maximum
        :return: None
        """
        for character in cls.data:
            character.stats.remaining_moves = character.stats.moves

    @classmethod
    def all_dead(cls) -> bool:
        """
        Checks if all instances characters of the class are dead or out of game
        :return:: True if all are dead or out of game, False otherwise
        """
        return len(cls.data) == 0


    def __init__(self):

        """
        Those are common attributes to all characters (Players and Monsters).
        Initialized to corresponding type when instantiating Player or Monster, except
        id, position, token and dungeon, initialized in DungeonLayout.place_item()
        Exclusive attributes of each class are added within corresponding classes.
        """
        self.char: str | None = None
        self.name: str | None = None
        self.id: int | None = None   # initialized in DungeonLayot.place_item()
        self.kind: str | None = None
        self.position: tuple[int:int] | None = None  # initialized in DungeonLayot.place_item()
        self.token: Token | None = None  # initialized in DungeonLayot.place_item()
        self.dungeon: DungeonLayout | None = None  # initialized in DungeonLayot.place_item()
        self.stats: CharacterStats | None = None
        self.blocked_by: tuple | None = None
        self.cannot_share_tile_with: tuple | None = None
        self.free_actions: tuple | None = None
        self.ignores: tuple | None = None
        self.inventory: dict[str:int] | None = None  # needed for MineMadnessGame_on_inv_object()
        self.ability_display: str | None = None  # needed for AbilityButton.display_text()


    def setup_character(self, position:tuple[int:int], dungeon: DungeonLayout):
        """
        Sets up the character when its CharacterToken is placed onto the tile
        :param tile: tile upon the CharacterToken is placed
        :param dungeon: dungeon in which the tile belongs
        :return: None
        """

        self.id = len(self.__class__.data)
        self.position = position
        self.dungeon = dungeon
        self.__class__.data.append(self)

    @abstractmethod
    def behave(self, tile: Tile) -> None:
        """
        Abstract method defining the behavior of a character when landing on a new tile
        :param tile: tile where character lands
        :return: None
        """
        pass

    @property
    def is_hidden(self) -> bool:  # needed for everybody for self.fight_on_tile()
        """
        Checks if the character is hidden
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
    def has_moved(self) -> bool:
        """
        Checks if the character has moved this turn
        :return: True if character has moved, False otherwise
        """
        return self.stats.remaining_moves < self.stats.moves

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
        :param opponent: opponent character
        :return: experience_when_killed of dead opponent
        """
        self.stats.remaining_moves -= 1
        damage = randint(self.stats.strength[0], self.stats.strength[1])
        damage = opponent.apply_toughness(damage)
        damage = self.enhance_damage(damage)

        if self.is_hidden:
            self.unhide()
        if opponent.is_hidden:
            opponent.unhide()

        opponent.stats.health = opponent.stats.health - damage
        opponent.token.show_damage()

        return opponent

    def kill_character(self, tile: Tile):
        """
        Removes the character from the game
        :param tile:: tile in which the character to kill is located
        :return: None
        """
        del self.__class__.data[self.id]
        self.__class__.rearrange_ids()
        tile.delete_token(self.token.kind)

    # MOVEMENT METHODS TO IMPLEMENT

    def glide(self):
        raise NotImplementedError()

    def walk(self):
        raise NotImplementedError()

    def stomp(self):
        raise NotImplementedError()
