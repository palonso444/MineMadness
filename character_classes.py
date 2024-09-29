from random import randint
from abc import ABC, abstractmethod


class Character(ABC):

    @classmethod
    def rearrange_ids(cls) -> None:

        for character in cls.data:
            character.id = cls.data.index(character)

    @classmethod
    def reset_moves(cls) -> None:

        for character in cls.data:
            character.stats.remaining_moves = character.stats.moves

    @classmethod
    def all_out_of_game(cls) -> bool:
        """
        Checks if all instances of the class (players or monsters) dead or out of game
        """

        if len(cls.data) == 0:
            return True
        return False

    @abstractmethod
    def enhance_damage(self, damage: int) -> int:
        """
        Enhances damage in combat (if applicable)
        """
        pass

    @abstractmethod
    def unhide(self) -> None:
        """
        Reverts hidden state of character
        """
        pass


    # INSTANCE METHODS

    def __init__(self):

        self.name: str | None = None
        self.inventory: dict | None = None
        self.id: int | None = None
        self.position: tuple | None = None

        # monsters need ability_active for the functioning of the ability_button
        self.ability_active: bool = False

        self.token = None
        self.dungeon = None

    def using_dynamite(self):  # needed for everybody for Token.on_slide_completed()
        return False

    def is_hidden(self):  # needed for everybody for self.fight_on_tile()
        return False

    def _apply_toughness(self, damage):  # needed for everybody for self.fight_on_tile()
        pass

    def update_position(self, position: tuple[int]) -> None:
        self.__class__.data[self.id].position = position

    def fight_on_tile(self, opponent_tile) -> bool:

        opponent = opponent_tile.get_character()
        self.stats.remaining_moves -= 1
        damage = randint(self.stats.strength[0], self.stats.strength[1])
        damage = opponent._apply_toughness(damage)

        damage = self.enhance_damage(damage)
        if self.is_hidden:
            self.unhide()

        opponent.stats.health = opponent.stats.health - damage
        if opponent.token.percentage_natural_health is not None:
            opponent.token.percentage_natural_health = (
                opponent.stats.health / opponent.stats.natural_health
            )

        self.dungeon.show_damage_token(
            opponent.token.shape.pos, opponent.token.shape.size
        )

        if opponent.stats.health <= 0:
            experience = opponent.experience_when_killed
            opponent.kill_character(opponent_tile)
            return experience

    def has_moved(self) -> bool:

        if self.stats.remaining_moves == self.stats.moves:
            return False
        return True

    def kill_character(self, tile):

        del self.__class__.data[self.id]
        self.__class__.rearrange_ids()
        tile.clear_token(self.token.kind)

    # MOVEMENT METHODS TO IMPLEMENT

    def glide(self):
        raise NotImplementedError()

    def walk(self):
        raise NotImplementedError()

    def stomp(self):
        raise NotImplementedError()
