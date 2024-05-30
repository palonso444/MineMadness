from kivy.uix.button import Button
from dataclasses import dataclass


@dataclass
class Effect:
    size: int
    duration: int


class Interfacebutton(Button):

    types = ("jerky", "coffee", "tobacco", "whisky", "talisman")

    def apply_cost(self, item):

        character = self.game.active_character

        character.inventory[item] -= 1
        self.game.inv_object = item

        character.stats.remaining_moves -= self.stats.use_time
        self.game.dynamic_movement_range()
        if character.stats.remaining_moves == 0:
            self.game.update_switch("character_done")


class JerkyButton(Interfacebutton):
    """
    Increases life
    """

    def on_release(self, *args):

        character = self.game.active_character

        character.stats.health += self.stats.effect_size
        (
            character.stats.health == character.stats.max_health
            if character.stats.health > character.stats.max_health
            else character.stats.health
        )

        self.game.update_switch("health")
        self.apply_cost("jerky")


class CoffeeButton(Interfacebutton):
    """
    Increases movement
    """

    def on_release(self, *args):

        character = self.game.active_character

        character.stats.remaining_moves = character.stats.moves
        character.stats.moves += self.stats.effect_size

        character.effects.append(
            Effect(size=self.stats.effect_size, duration=self.stats.effect_duration)
        )

        self.apply_cost("coffee")


class TobaccoButton(Interfacebutton):
    """
    Increases thoughness (armor-like effect)
    """

    pass


class WhiskyButton(Interfacebutton):
    """
    Increases strength
    """

    pass


class TalismanButton(Interfacebutton):
    """
    Revives a random character from the death ones, if any
    Otherwise, levels up the character that uses it
    """

    pass
