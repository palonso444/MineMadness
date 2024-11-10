from docutils.nodes import transition
from kivy.app import App  # type: ignore
from kivy.uix.boxlayout import BoxLayout  # type: ignore

# from kivy.core.text import LabelBase    # type: ignore
# from kivy.uix.image import Image    # type: ignore
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty  # type: ignore
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.core.audio import SoundLoader

import player_classes as players
import monster_classes as monsters
from interface import Interfacebutton
from dungeon_classes import DungeonLayout


# LabelBase.register(name = 'Vollkorn',
# fn_regular= 'fonts/Vollkorn-Regular.ttf',
# fn_italic='fonts/Vollkorn-Italic.ttf'

class MainMenu(Screen):
    pass

class HowToPlay(Screen):
    pass

class GameOver(Screen):
    pass


class MineMadnessGame(Screen):  # initialized in kv file

    # GENERAL PROPERTIES
    level = NumericProperty(None)
    dungeon = ObjectProperty(None)
    turn = NumericProperty(None, allownone=True)
    active_character_id = NumericProperty(None, allownone=True)
    character_done = BooleanProperty(False)
    player_exited = BooleanProperty(False)

    # ABILITY PROPERTIES
    ability_button = BooleanProperty(False)

    # INVENTORY PROPERTIES
    inv_object = StringProperty(None, allownone=True)

    # LABEL PROPERTIES
    health = BooleanProperty(None)
    shovels = BooleanProperty(None)
    weapons = BooleanProperty(None)
    gems = BooleanProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level: int = 1
        self.active_character: Character | None = None  # defined by MineMadnessGame.on_active_character_id()
        self.total_gems: int | None = None  # defined by MineMadnessGame.DungeonLayout.on_pos()

    @staticmethod
    def on_dungeon(game, dungeon):

        game.total_gems = game.dungeon.stats.gem_number()  # self.game defined in kv file
        players.Player.gems = 0
        players.Player.set_starting_player_order()
        game.initialize_switches()
        for player in players.Player.data:
            player.remove_all_effects(game.turn)
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
        elif switch_name == "active_character_id":
            switch_value = self.active_character_id
            setattr(self, switch_name, None)

        setattr(self, switch_name, switch_value)

    def update_experience_bar(self):
        """
        Updates the range of the experience bar according to the current active character.
        :return: None
        """
        if isinstance(self.active_character, players.Player):
            self.ids.experience_bar.max = self.active_character.stats.exp_to_next_level
            self.ids.experience_bar.value = self.active_character.experience
        else:
            self.ids.experience_bar.value = 0

    def on_ability_button(self, *args):
        """
        Updates the state of the ability button depending on the circumstances of the game.
        :param args: needed for the functioning of the callback. Args are: game instance and a boolean value of
        the corresponding switch.
        :return: None
        """
        self.ability_button_active = False

        if isinstance(self.active_character, monsters.Monster):
            self.ids.ability_button.disabled = True
            self.ids.ability_button.state = "normal"

        elif isinstance(self.active_character, players.Player):
            self.ids.ability_button.disabled = not self.ids.ability_button.condition_active
            self.ids.ability_button.state = "down" if self.active_character.ability_active else "normal"

        self.ability_button_active = True

    def on_character_done(self, *args):
        """
        Checks what to do when a character finishes a movement, but it may still have movements left
        :param args: needed for the functioning of the callback. Args are: game instance and a boolean value of
        the corresponding switch
        :return: None
        """
        if monsters.Monster.all_dead() and self.active_character.stats.remaining_moves == 0:
            self.active_character.stats.remaining_moves = self.active_character.stats.moves
            self.active_character.remove_effects_if_over(self.turn)
            self.active_character.token.unselect_token()
            self.update_switch("turn")

        if isinstance(self.active_character, players.Player) and self.active_character.stats.remaining_moves > 0:
            if self.active_character.using_dynamite:
                self.activate_accessible_tiles(self.active_character.stats.shooting_range)
            else:
                self.activate_accessible_tiles(self.active_character.stats.remaining_moves)

        else:  # if self.active_character remaining moves == 0
            if isinstance(self.active_character, players.Player):
                self.active_character.remove_effects_if_over(self.turn)
                self.active_character.token.unselect_token()
            self.next_character()  # switch turns if character last of character.characters

    @staticmethod
    def on_turn(game, turn):
        """
        On new turn, resets movements of the characters (monsters or players). Sets self.active_character_id to 0
        and updates it if the value was already 0 (there is only one character left).
        :param game: current instance of the game.
        :param turn: turn number (even for players, odd for monsters).
        :return: None
        """
        if turn is not None:

            if turn % 2 == 0 or monsters.Monster.all_dead():
                players.Player.reset_moves()
            else:
                monsters.Monster.reset_moves()

            if game.active_character_id == 0:
                game.update_switch("active_character_id")
            else:
                game.active_character_id = 0

    @staticmethod
    def on_active_character_id(game, character_id):
        """
        Checks what to do when the active character changes.
        :param game: current instance of the game.
        :param character_id: id of the new active character.
        :return: None
        """
        if character_id is not None:
            # if player turn or no monsters
            if game.turn % 2 == 0 or monsters.Monster.all_dead():
                game.active_character = players.Player.data[character_id]

                if game.active_character.has_moved and not monsters.Monster.all_dead():
                    game.next_character()

                else:
                    game.active_character.token.select_character()
                    game.update_interface()
                    # health must be updated here after setting player as active character
                    game.update_switch("health")
                    game.update_switch("shovels")
                    game.update_switch("weapons")

                    if game.active_character.using_dynamite:
                        game.activate_accessible_tiles(game.active_character.stats.shooting_range)
                    else:
                        game.activate_accessible_tiles(game.active_character.stats.remaining_moves)

            else:  # if monsters turn and monsters in the game
                game.dungeon.disable_all_tiles()  # tiles deactivated in monster turn
                game.active_character = monsters.Monster.data[game.active_character_id]
                game.update_interface()
                game.update_switch("health")
                game.active_character.token.select_character()
                game.active_character.move()

    def on_player_exited(self, *args):
        """
        Handles the change of level or turn when the active character exits the level.
        :param args: needed for the functioning of then callback. Args are: game instance and a boolean value of
        the corresponding switch.
        :return: None
        """
        # in this case all out of game
        if players.Player.all_dead():
            monsters.Monster.data.clear()
            self.level += 1
            self.generate_next_level(self.level)

        elif self.active_character_id == len(players.Player.data):
            self.update_switch("turn")

        else:
            self.update_switch("active_character_id")

    def next_character(self):
        if self.active_character.id < len(self.active_character.__class__.data) - 1:
            self.active_character_id += 1  # next character on list moves

        else:  # if end of characters list reached (all have moved)
            self.update_switch("turn")

    def activate_accessible_tiles(self, steps:int) -> None:
        """
        Gets the total range of activable tiles (player movement range and other player positions if player.
        did not move if monsters are present, otherwise all other players positions).
        :param steps: number of steps within which accessible Tiles must be activated
        :return: None
        """

        if monsters.Monster.all_dead():
            players_not_yet_active = {
                player.token.position for player in players.Player.data
            }
        else:
            players_not_yet_active = {
                player.token.position
                for player in players.Player.data
                if not player.has_moved
            }

        self.dungeon.disable_all_tiles()
        player_movement_range = self.dungeon.get_range(self.active_character.get_position(), steps)
        positions_in_range = players_not_yet_active.union(player_movement_range)
        self.dungeon.enable_tiles(positions_in_range, self.active_character)

    def switch_character(self, new_active_character):
        """
        Changes the active character (self.active_character).
        :param new_active_character: character to be activated.
        :return: None
        """
        index_new_char = players.Player.data.index(new_active_character)
        index_old_char = players.Player.data.index(self.active_character)
        players.Player.swap_characters(index_new_char,index_old_char)

        self.active_character.token.unselect_token()
        self.active_character = new_active_character
        self.active_character_id = None
        self.active_character_id = players.Player.data.index(self.active_character)

    @staticmethod
    def on_inv_object(game, inv_object):
        """
        When a character picks up an object enables the corresponding button if applicable.
        :param game: current instance of the game.
        :param inv_object: object of the inventory just picked up.
        :return: None
        """
        if inv_object is not None:

            character = game.active_character

            if character.inventory is None or character.inventory[inv_object] == 0:
                game.ids[inv_object + "_button"].disabled = True
            else:
                game.ids[inv_object + "_button"].disabled = False

            # needs to be reset to None otherwise it is not possible to pick 2 equal objects in a row
            game.inv_object = None

    def generate_next_level(self, new_dungeon_level: int) -> None:
        """
        Removed current level board and generates instantiates a new one
        :param new_dungeon_level: number of the next level
        :return: None
        """
        scrollview = self.children[0].children[0]
        scrollview.remove_widget(self.dungeon)
        scrollview.add_widget(DungeonLayout(game=self))
        self.turn = None


class CrapgeonApp(App):

    music_on = BooleanProperty(None)
    game_mode_normal = BooleanProperty(None)

    def __init__(self):
        super().__init__()
        self.music = SoundLoader.load("./music/stocktune_eternal_nights_embrace.ogg")
        self.music.loop = True
        self.music_on = False
        self.game_mode_normal = True

    def build(self):
        app = ScreenManager(transition=FadeTransition(duration=0.3))
        app.add_widget(MainMenu(name='main_menu'))
        app.add_widget(MineMadnessGame(name='game_screen'))
        app.add_widget(HowToPlay(name="how_to_play"))
        app.add_widget(GameOver(name="game_over"))
        return app

    @staticmethod
    def on_music_on(app, music_on):

        if music_on:
            app.music.volume = 1
            app.music.play()
        else:
            app.music.stop()


######################################################### START APP ###################################################


if __name__ == "__main__":
    CrapgeonApp().run()
