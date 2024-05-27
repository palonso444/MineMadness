from kivy.uix.button import Button


class Interfacebutton(Button):

    types = ("jerky", "tobacco", "whisky", "talisman")

    def apply_cost(self, item):

        character = self.game.active_character

        character.inventory[item] -= 1
        self.game.inv_object = item

        character.stats.remaining_moves -= 1
        self.game.dynamic_movement_range()
        if character.stats.remaining_moves == 0:
            self.game.update_switch("character_done")


class JerkyButton(Interfacebutton):

    def on_release(self, *args):

        character = self.game.active_character

        character.stats.health += 2
        (
            character.stats.health == character.stats.max_health
            if character.stats.health > character.stats.max_health
            else character.stats.health
        )

        self.game.update_switch("health")
        self.apply_cost("jerky")


class TobaccoButton(Interfacebutton):
    pass


class WhiskyButton(Interfacebutton):
    pass


class TalismanButton(Interfacebutton):
    pass
