from kivy.uix.button import Button
from dataclasses import dataclass


class Interfacebutton(Button):

    types = ("jerky", "coffee", "tobacco", "whisky", "talisman")

    def apply_cost(self, item):

        character = self.game.active_character

        character.inventory[item] -= 1
        self.game.inv_object = item  # this disables the button, if necessary

        character.stats.remaining_moves -= self.stats.use_time
        self.game.dynamic_movement_range()

        character.check_if_overdose(item)

        if character.stats.remaining_moves == 0:
            self.game.update_switch("character_done")

    def get_effect_size(self, character, attribute: str):

        target_attribute = getattr(character.stats, attribute)

        effect_size = int(self.stats.effect_size * target_attribute)

        effect_size = (
            effect_size
            if effect_size > self.stats.min_effect
            else self.stats.min_effect
        )
        effect_size = (
            effect_size
            if self.stats.max_effect is None or effect_size < self.stats.max_effect
            else self.stats.max_effect
        )

        return effect_size


class JerkyButton(Interfacebutton):
    """
    Increases life
    """

    def on_release(self, *args):

        character = self.game.active_character

        effect_size = self.get_effect_size(character, "max_health")

        character.stats.health += (
            effect_size
            if character.stats.health + effect_size <= character.stats.max_health
            else character.stats.max_health
        )

        self.game.update_switch("health")
        self.apply_cost("jerky")


class CoffeeButton(Interfacebutton):
    """
    Increases movement
    """

    def on_release(self, *args):

        character = self.game.active_character

        effect_size = self.get_effect_size(character, "natural_moves")

        character.stats.moves += effect_size
        character.stats.remaining_moves += effect_size

        character.effects["moves"].append(
            {
                "size": effect_size,
                "end_turn": self.game.turn + self.stats.effect_duration,
            }
        )

        self.apply_cost("coffee")


class TobaccoButton(Interfacebutton):
    """
    Increases thoughness (armor-like effect)
    """

    def on_release(self, *args):

        character = self.game.active_character

        effect_size = self.get_effect_size(character, "max_health")

        character.stats.thoughness += effect_size

        character.effects["thoughness"].append(
            {
                "size": effect_size,
                "end_turn": self.game.turn + self.stats.effect_duration,
            }
        )

        self.apply_cost("tobacco")


class WhiskyButton(Interfacebutton):
    """
    Increases strength
    """

    def on_release(self, *args):

        character = self.game.active_character

        effect_size = (
            character.natural_strength[0] + character.natural_strength[1]
        ) // 2
        effect_size = (
            effect_size
            if effect_size > self.stats.min_effect
            else self.stats.min_effect
        )

        character.stats.strength[1] = character.stats.strength[1] + effect_size

        character.effects["strength"].append(
            {
                "size": effect_size,
                "end_turn": self.game.turn + self.stats.effect_duration,
            }
        )

        self.apply_cost("whisky")


class TalismanButton(Interfacebutton):
    """
    Revives a random character from the death ones, if any
    Otherwise, levels up the character that uses it
    """

    pass
