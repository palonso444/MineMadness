from kivy.app import App  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore
from kivy.uix.gridlayout import GridLayout  # type: ignore

# from kivy.uix.scrollview import ScrollView  # type: ignore
# from kivy.uix.label import Label    # type: ignore
from kivy.uix.button import Button  # type: ignore

# from kivy.core.text import LabelBase    # type: ignore
# from kivy.uix.image import Image    # type: ignore
# from kivy.graphics import Ellipse, Rectangle   # type: ignore
# from kivy.uix.widget import Widget  # type: ignore
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty  # type: ignore

import character_classes as characters
import interface


# LabelBase.register(name = 'Vollkorn',
# fn_regular= 'fonts/Vollkorn-Regular.ttf',
# fn_italic='fonts/Vollkorn-Italic.ttf'


class CrapgeonGame(BoxLayout):  # initlialized in kv file

    # GENERAL PROPERTIES
    dungeon = ObjectProperty(None)
    turn = BooleanProperty(None)
    active_character_id = NumericProperty(None, allownone=True)
    character_done = BooleanProperty(False)
    player_exited = BooleanProperty(False)
    # self.active_character -> initialized and defined by on_active_character_id()
    # self.total_gems -> initialized and defined by DungeonLayout.on_pos()

    # INVENTORY PROPERTIES
    inv_object = StringProperty(None, allownone=True)

    # LABEL PROPERTIES
    health = BooleanProperty(None)
    shovels = BooleanProperty(None)
    weapons = BooleanProperty(None)
    gems = BooleanProperty(None)

    def initialize_switches(self):

        self.turn = True  # TRUE for players, FALSE for monsters. Player starts

        self.health = False
        self.shovels = False
        self.weapons = False
        self.gems = False

    def update_switch(self, switch_name):

        switch_value = getattr(self, switch_name)
        switch_value = not switch_value
        setattr(self, switch_name, switch_value)

    def update_interface(self):

        for button_type in interface.Interfacebutton.types:
            self.inv_object = button_type

    def on_dungeon(self, *args):

        characters.Player.gems = 0
        self.dungeon.match_blueprint()
        self.initialize_switches()
        characters.Player.exited.clear()

    def on_character_done(self, *args):

        if (
            isinstance(self.active_character, characters.Player)
            and self.active_character.stats.remaining_moves > 0
        ):
            self.dynamic_movement_range()  # checks if player can still move

        else:
            self.next_character()  # switch turns if character last of character.characters

    def on_turn(self, *args):

        if self.turn or len(characters.Monster.data) == 0:
            characters.Player.reset_moves()
        else:
            characters.Monster.reset_moves()

        if self.active_character_id == 0:
            self.active_character_id = None

        self.active_character_id = 0

    def on_active_character_id(self, *args):

        if type(self.active_character_id) is int:

            if (
                self.turn or len(characters.Monster.data) == 0
            ):  # if player turn or no monsters
                self.active_character = characters.Player.data[self.active_character_id]

                if self.active_character.has_moved():
                    self.next_character()

                else:
                    self.update_interface()
                    self.update_switch(
                        "health"
                    )  # must be updated here after seting player as active character
                    self.update_switch("shovels")
                    self.update_switch("weapons")
                    self.dynamic_movement_range()

            elif not self.turn:  # if monsters turn and monsters in the game

                self.dungeon.activate_which_tiles()  # tiles deactivated in monster turn
                self.active_character = characters.Monster.data[
                    self.active_character_id
                ]
                self.update_interface()
                self.update_switch("health")
                self.active_character.token.move_monster()

    def on_player_exited(self, *args):

        exit_tile = self.dungeon.get_tile(self.active_character.position)

        exited_player = characters.Player.data.pop(self.active_character_id)
        characters.Player.exited.add(exited_player)
        self.active_character.rearrange_ids()
        exit_tile.clear_token("player")

        if len(characters.Player.data) == 0:

            characters.Monster.data.clear()
            app = App.get_running_app()  # maybe this can be done from dungeon not app
            app.level += 1  # this should be self.dungeon.stats.level
            app.generate_next_level()  # maybe this can be done from dungeon not app

        elif self.active_character_id == len(characters.Player.data):
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

    def dynamic_movement_range(self):

        players_not_yet_active = set()

        for player in characters.Player.data:

            if not player.has_moved():
                players_not_yet_active.add(player.position)

        player_movement_range = self.active_character.get_movement_range(self.dungeon)
        positions_in_range = players_not_yet_active.union(player_movement_range)
        self.dungeon.activate_which_tiles(positions_in_range)

    def switch_character(self, new_active_character):

        index_new_char = characters.Player.data.index(new_active_character)
        index_old_char = characters.Player.data.index(self.active_character)
        (
            characters.Player.data[index_old_char],
            characters.Player.data[index_new_char],
        ) = (
            characters.Player.data[index_new_char],
            characters.Player.data[index_old_char],
        )

        self.active_character.rearrange_ids()
        self.active_character = new_active_character
        self.active_character_id = None
        self.active_character_id = characters.Player.data.index(self.active_character)

    def on_inv_object(self, *args):

        if self.inv_object is not None:

            character = self.active_character

            if character.inventory is None or character.inventory[self.inv_object] == 0:
                self.ids[self.inv_object + "_button"].disabled = True
            else:
                self.ids[self.inv_object + "_button"].disabled = False

            self.inv_object = None


class CrapgeonApp(App):

    level = 1

    def build(self):
        return CrapgeonGame()

    def generate_next_level(self):

        self.root.clear_widgets()  # self root is root widget, in this case CrapgeonGame object
        new_level = CrapgeonGame()
        self.root.add_widget(new_level)


######################################################### START APP ##########################################################


if __name__ == "__main__":
    CrapgeonApp().run()
