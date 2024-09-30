from kivy.app import App  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore

# from kivy.core.text import LabelBase    # type: ignore
# from kivy.uix.image import Image    # type: ignore
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty  # type: ignore

import player_classes as players
import monster_classes as monsters
from interface import Interfacebutton
from crapgeon_utils import check_if_multiple
from dungeon_classes import DungeonLayout


# LabelBase.register(name = 'Vollkorn',
# fn_regular= 'fonts/Vollkorn-Regular.ttf',
# fn_italic='fonts/Vollkorn-Italic.ttf'


class MineMadnessGame(BoxLayout):  # initialized in kv file

    # GENERAL PROPERTIES
    dungeon = ObjectProperty(None)
    turn = NumericProperty(None, allownone=True)
    active_character_id = NumericProperty(None, allownone=True)
    character_done = BooleanProperty(False)
    player_exited = BooleanProperty(False)
    # self.active_character -> initialized and defined by on_active_character_id()
    # self.total_gems -> initialized and defined by DungeonLayout.on_pos()

    # ABILITY PROPERTIES
    ability_button = BooleanProperty(False)
    # ability_button_active initialized by initialize_switches

    # INVENTORY PROPERTIES
    inv_object = StringProperty(None, allownone=True)

    # LABEL PROPERTIES
    health = BooleanProperty(None)
    shovels = BooleanProperty(None)
    weapons = BooleanProperty(None)
    gems = BooleanProperty(None)

    @staticmethod
    def on_dungeon(game, dungeon):

        players.Player.gems = 0
        dungeon.match_blueprint()
        # characters.Player.set_starting_player_order()
        game.initialize_switches()
        players.Player.exited.clear()

    def initialize_switches(self):

        self.turn = 0  # even for players, odd for monsters. Player starts

        self.health = False
        self.shovels = False
        self.weapons = False
        self.gems = False

        self.ability_button_active = True  # TODO: when button unbinding in self.on_ability_button() works this has to go

    def update_interface(self):

        for button_type in Interfacebutton.types:
            self.inv_object = button_type
        self.update_switch("ability_button")
        self.update_experience_bar()

    def update_switch(self, switch_name):

        switch_value = getattr(self, switch_name)
        if isinstance(switch_value, bool):
            switch_value = not switch_value
        elif switch_name == "turn":
            switch_value += 1
        setattr(self, switch_name, switch_value)

    def update_experience_bar(self):

        if isinstance(self.active_character, players.Player):
            self.ids.experience_bar.max = self.active_character.stats.exp_to_next_level
            self.ids.experience_bar.value = self.active_character.experience
        else:
            self.ids.experience_bar.value = 0

    def on_ability_button(self, *args):

        self.ability_button_active = False  # TODO: unbind button instead of this

        if isinstance(self.active_character, monsters.Monster):
            self.ids.ability_button.disabled = True
            self.ids.ability_button.state = "normal"

        elif self.active_character.ability_active:
            self.ids.ability_button.disabled = False
            self.ids.ability_button.state = "down"

        elif isinstance(self.active_character, players.Sawyer):
            if self.active_character.special_items["powder"] > 0:
                self.ids.ability_button.disabled = False
            else:
                self.ids.ability_button.disabled = True
            self.ids.ability_button.state = "normal"

        elif isinstance(self.active_character, players.Hawkins):
            if self.active_character.special_items["dynamite"] > 0:
                self.ids.ability_button.disabled = False
            else:
                self.ids.ability_button.disabled = True
            self.ids.ability_button.state = "normal"

        elif isinstance(self.active_character, players.CrusherJane):
            if self.active_character.stats.weapons > 0:
                self.ids.ability_button.disabled = False
            else:
                self.ids.ability_button.disabled = True
            self.ids.ability_button.state = "normal"

        self.ability_button_active = True  # TODO: bind button instead of this

    def on_character_done(self, *args):

        # if no monsters in game, players can move indefinitely
        if (
            isinstance(self.active_character, players.Player)
            and self.active_character.stats.remaining_moves == 0
            and monsters.Monster.all_dead()
        ):
            self.active_character.stats.remaining_moves = (
                self.active_character.stats.moves
            )

        if (
            isinstance(self.active_character, players.Player)
            and self.active_character.stats.remaining_moves > 0
        ):
            if self.active_character.using_dynamite():
                self.dynamic_movement_range("shooting")
            else:
                self.dynamic_movement_range()  # checks if player can still move

        else:  # if self.active_character remaining moves == 0
            if isinstance(self.active_character, players.Player):
                self.active_character.remove_effects(self.turn)
                self.active_character.token.remove_selection_circle()
            self.next_character()  # switch turns if character last of character.characters

    def on_turn(self, game, turn):

        if turn is not None:

            if check_if_multiple(turn, 2) or monsters.Monster.all_dead():
                players.Player.reset_moves()
            else:
                monsters.Monster.reset_moves()

            if self.active_character_id == 0:
                self.active_character_id = None

            self.active_character_id = 0

    def on_active_character_id(self, game, character_id):

        if character_id is not None:

            if (
                check_if_multiple(self.turn, 2)
                or monsters.Monster.all_dead()
            ):  # if player turn or no monsters
                self.active_character = players.Player.data[character_id]

                if (
                    self.active_character.has_moved()
                    and not monsters.Monster.all_dead()
                ):
                    self.next_character()

                else:
                    self.active_character.token.draw_selection_circle()
                    self.update_interface()
                    self.update_switch(
                        "health"
                    )  # must be updated here after seting player as active character
                    self.update_switch("shovels")
                    self.update_switch("weapons")

                    if self.active_character.using_dynamite():
                        self.dynamic_movement_range("shooting")
                    else:
                        self.dynamic_movement_range()

            else:  # if monsters turn and monsters in the game

                self.dungeon.activate_which_tiles()  # tiles deactivated in monster turn
                self.active_character = monsters.Monster.data[
                    self.active_character_id
                ]
                self.update_interface()
                self.update_switch("health")
                self.active_character.token.move_monster()

    def on_player_exited(self, *args):

        exit_tile = self.dungeon.get_tile(self.active_character.position)

        exited_player = players.Player.data.pop(self.active_character_id)
        players.Player.exited.add(exited_player)
        self.active_character.rearrange_ids()
        exit_tile.clear_token("player")

        if players.Player.all_dead():

            monsters.Monster.data.clear()
            new_dungeon_level: int = self.dungeon.dungeon_level + 1
            self.generate_next_level(new_dungeon_level)

        elif self.active_character_id == len(players.Player.data):
            self.update_switch("turn")

        else:
            temp = self.active_character_id
            self.active_character_id = None
            self.active_character_id = temp

    def next_character(self):

        if self.active_character.id < len(self.active_character.__class__.data) - 1:
            self.active_character_id += 1  # next character on list moves

        else:  # if end of characters list reached (all have moved)
            self.update_switch("turn")

    def dynamic_movement_range(self, range_kind: str = "movement"):
        """
        Gets total range of activable tiles (player movement range and other player positions if player
        did not move if monsters are present, otherwhise all other players positions) and pass it to
        activate_which_tiles() to check if tiles are activable
        """

        if monsters.Monster.all_dead():
            players_not_yet_active = {
                player.position for player in players.Player.data
            }
        else:
            players_not_yet_active = {
                player.position
                for player in players.Player.data
                if not player.has_moved()
            }

        player_movement_range = self.active_character.get_range(
            self.dungeon, range_kind
        )
        positions_in_range = players_not_yet_active.union(player_movement_range)
        self.dungeon.activate_which_tiles(positions_in_range)

    def switch_character(self, new_active_character):

        index_new_char = players.Player.data.index(new_active_character)
        index_old_char = players.Player.data.index(self.active_character)
        (
            players.Player.data[index_old_char],
            players.Player.data[index_new_char],
        ) = (
            players.Player.data[index_new_char],
            players.Player.data[index_old_char],
        )
        players.Player.rearrange_ids()
        self.active_character.token.remove_selection_circle()
        self.active_character = new_active_character
        self.active_character_id = None
        self.active_character_id = players.Player.data.index(self.active_character)

    def on_inv_object(self, game, inv_object):

        if inv_object is not None:

            character = self.active_character

            if character.inventory is None or character.inventory[inv_object] == 0:
                self.ids[inv_object + "_button"].disabled = True
            else:
                self.ids[inv_object + "_button"].disabled = False

            self.inv_object = None

    def generate_next_level(self, new_dungeon_level: int) -> None:

        self.children[0].remove_widget(self.dungeon)  # self.children[0] is Scrollview
        new_level = DungeonLayout(dungeon_level=new_dungeon_level, game=self)
        self.children[0].add_widget(new_level)
        self.turn = None


class CrapgeonApp(App):

    def build(self):
        return MineMadnessGame()


######################################################### START APP ##########################################################


if __name__ == "__main__":
    CrapgeonApp().run()
