from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from random import choice

from player_classes import Player


class AbilityButton(ToggleButton):

    @property
    def condition_active(self):
        character = self.game.active_character
        # for the moment there is only one special item
        return (character.special_items[list(character.special_items.keys())[0]] > 0
                or self.game.active_character.ability_active)

    def on_state(self, instance, value):

        if self.game.ability_button_active:
            # TODO: when button unbinding in self.game.on_ability_button() works this has to go

            character = self.game.active_character

            if value == "down":
                match character.species:

                    case "sawyer":
                        character.hide()

                    case "hawkins":
                        character.token.show_effect_token("dynamite")
                        character.ability_active = True
                        self.game.activate_accessible_tiles(character.stats.shooting_range)

                    case "crusherjane":
                        character.token.show_effect_token("armed")
                        character.ability_active = True
                        character.remaining_moves -= 1

            elif value == "normal":
                match character.species:

                    case "sawyer":
                        character.unhide()
                        self.game.activate_accessible_tiles(character.remaining_moves)  # can dig again

                    case "hawkins":
                        character.ability_active = False
                        self.game.activate_accessible_tiles(character.remaining_moves)

                    case "crusherjane":
                        character.token.show_effect_token("armed", effect_ends=True)
                        character.ability_active = False


class Interfacebutton(Button):

    types = ("jerky", "coffee", "tobacco", "whisky", "talisman")

    def apply_cost(self, item):

        character = self.game.active_character
        character.inventory[item] -= 1
        self.game.inv_object = item  # this disables the button, if necessary

        character.remaining_moves -= self.stats.use_time
        self.game.activate_accessible_tiles(character.remaining_moves)

        character.check_if_overdose(item)

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

    def on_release(self):

        character = self.game.active_character
        effect_size = self.get_effect_size(character, "natural_health")
        character.heal(effect_size)
        character.token.show_effect_token("heal")
        # this updates health bar
        character.token.bar_length = character.stats.health / character.stats.natural_health
        self.apply_cost("jerky")


class CoffeeButton(Interfacebutton):
    """
    Increases movement
    """

    def on_release(self):

        character = self.game.active_character
        effect_size = self.get_effect_size(character, "natural_moves")
        character.stats.moves += effect_size
        character.remaining_moves += effect_size
        character.effects["moves"].append(
            {
                "size": effect_size,
                "end_turn": self.game.turn + self.stats.effect_duration,
            }
        )
        character.token.show_effect_token("moves")
        self.apply_cost("coffee")


class TobaccoButton(Interfacebutton):
    """
    Increases toughness (armor-like effect)
    """

    def on_release(self):

        character = self.game.active_character
        effect_size = self.get_effect_size(character, "natural_health")
        character.stats.toughness += effect_size
        character.effects["toughness"].append(
            {
                "size": effect_size,
                "end_turn": self.game.turn + self.stats.effect_duration,
            }
        )
        character.token.show_effect_token("toughness")
        self.apply_cost("tobacco")


class WhiskyButton(Interfacebutton):
    """
    Increases strength
    """

    def on_release(self):

        character = self.game.active_character
        effect_size = int(
            (character.stats.natural_strength[0] + character.stats.natural_strength[1]) / 2
            * self.stats.effect_size
        )
        effect_size = (
            effect_size
            if effect_size > self.stats.min_effect
            else self.stats.min_effect
        )
        character.stats.strength[1] += effect_size
        character.effects["strength"].append(
            {
                "size": effect_size,
                "end_turn": self.game.turn + self.stats.effect_duration,
            }
        )

        character.token.show_effect_token("strength")
        self.apply_cost("whisky")


class TalismanButton(Interfacebutton):
    """
    Revives a random character from the death ones, if any
    Otherwise, levels up the character that uses it
    """

    def on_release(self):

        character = self.game.active_character
        if Player.all_players_alive():
            character = self.game.active_character
            character.experience = character.stats.exp_to_next_level

            character.token.show_effect_token("level_up")

        else:
            player = choice(Player.dead)
            player.resurrect(character.get_dungeon())
            player.token.show_effect_token("resurrect")

        self.apply_cost("talisman")
