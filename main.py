from __future__ import annotations

from kivy.app import App  # type: ignore
from kivy.lang import Builder
from kivy.core.text import LabelBase
# from kivy.uix.image import Image    # type: ignore
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty  # type: ignore
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.audio import SoundLoader
from json import dump, load
from os.path import exists
from os import remove

from dungeon_blueprint import Blueprint
from player_classes import Player, Sawyer, Hawkins, CrusherJane  # players needed for globals()
import monster_classes as monsters
from dungeon_classes import DungeonLayout
from minemadness_screens import MineMadnessGame, MainMenu, HowToPlay, GameOver, OutGameOptions, InGameOptions, NewGameConfig

LabelBase.register(name = 'duality', fn_regular= 'fonts/duality.ttf')
LabelBase.register(name = 'edmunds', fn_regular= 'fonts/edmunds_distressed.ttf')

class MineMadnessApp(App):

    music_on = BooleanProperty(None)
    game_mode_normal = BooleanProperty(None)
    ongoing_game = BooleanProperty(False)
    level = NumericProperty(None)
    saved_game = BooleanProperty(False)
    game_over_message = StringProperty(None)

    def __init__(self):
        super().__init__()
        self.game_mode_normal: bool = True
        self.saved_game_file: str = "saved_game.json"
        self.saved_game: bool = exists("saved_game.json")

        self.music = SoundLoader.load("./music/stocktune_eternal_nights_embrace.ogg")
        self.music.loop = True
        self.music_on: bool = False

        self.game: MineMadnessGame | None = None
        self.sm: ScreenManager | None = None

    def build(self) -> ScreenManager:
        Builder.load_file("how_to_play.kv")
        self.sm = ScreenManager(transition=FadeTransition(duration=0.3))
        self.sm.add_widget(MainMenu(name="main_menu"))
        self.sm.add_widget(HowToPlay(name="how_to_play"))
        self.sm.add_widget(GameOver(name="game_over"))
        self.sm.add_widget(OutGameOptions(name="out_game_options"))
        self.sm.add_widget(InGameOptions(name="in_game_options"))
        self.sm.add_widget(NewGameConfig(name="new_game_config"))
        self.sm.current = "main_menu"
        return self.sm

    def add_dungeon_to_game(self, dungeon: DungeonLayout | None = None) -> None:
        """
        Adds a dungeon to MineMadnessGame
        :param dungeon: DungeonLayout to add. If None, a random one according to MineMadnessApp.game.level is generated
        :return: None
        """
        scrollview = self.game.children[0].children[1]
        if dungeon is None:
            scrollview.add_widget(DungeonLayout(game=self.game))
        else:
            scrollview.add_widget(dungeon)

    def remove_dungeon_from_game(self) -> None:
        """
        Removes the dungeon from MineMadnessGame
        :return: None
        """
        scrollview = self.game.children[0].children[1]
        scrollview.remove_widget(self.game.dungeon)

    def _clean_previous_game(self) -> None:
        """
        Cleans the data from the previous MineMadnessGame and removes it from the ScreenManager
        :return: None
        """
        Player.clear_character_data()
        monsters.Monster.clear_character_data()
        self.sm.remove_widget(self.sm.get_screen("game_screen"))

    def start_new_game(self) -> None:
        if self.saved_game:
            remove(self.saved_game_file)
            self.saved_game = False
        if self.sm.has_screen("game_screen"):
            self._clean_previous_game()
        self.game = MineMadnessGame(name="game_screen")
        self.ongoing_game = True
        self._setup_dungeon_screen()

    def _setup_dungeon_screen(self, dungeon: DungeonLayout | None = None) -> None:
        """
        Adds a new dungeon to MineMadnessGame
        :param dungeon: dungeon to add. If None, a random one is added
        :return: None
        """
        self.add_dungeon_to_game(dungeon)
        self.sm.add_widget(self.game)
        self.sm.current = "game_screen"

    def save_game(self) -> None:
        with open(self.saved_game_file, "w") as f:
            dump(self._get_game_state(), f, indent=4)
        self.saved_game = True

    def _get_game_state(self) -> dict:
        """
        Captures the state of the dungeon (blueprint) and the data of alive and dead players
        and stores everything into a dictionary. ONLY WORKS IF USED AT THE VERY BEGINNING OF LEVEL,
        NOT ONCE THE LEVEL STARTED
        :return: dictionary with the state of the game (blueprint, alive players, dead players)
        """
        game_state = dict()
        game_state["level"] = self.game.level
        game_state["game_mode_normal"] = self.game_mode_normal
        game_state["blueprint"] = self.game.dungeon.blueprint.to_dict()

        # keys must be converted from tuple to str in order to be JSON encoded
        game_state["torches_dict"] = {str(key): value for key,value in self.game.dungeon.torches_dict.items()}\
                                        if self.game.dungeon.torches_dict is not None else None

        game_state["players_alive"] = {player.__class__.__name__: player.to_dict() for player in Player.data}
        game_state["players_dead"] = {player.__class__.__name__: player.to_dict() for player in Player.dead_data}
        return game_state

    def continue_game_or_load(self) -> None:
        """
        Regulates the function of the ContinueButton defined in the kv file
        :return: None
        """
        if self.ongoing_game:
            self.sm.current = "game_screen"
        else:
            self.load_game()

    def load_game(self) -> None:
        """
        Loads the game from the JSON file, cleans the previous one and generated Player.data and Player.dead_data
        :return: None
        """
        with open(self.saved_game_file, "r") as f:
            data = load(f)

        # torches dict keys are str and need to be converted to tuple
        if data["torches_dict"] is not None:
            data["torches_dict"] = {(int(key[1]), int(key[4])): value
                                    for key, value in data["torches_dict"].items()}
        #level_track are nested dict and keys are str which must be converted to int
        data = self._convert_all_digit_keys_to_int(data)

        self.game_mode_normal = data["game_mode_normal"]
        if self.sm.has_screen("game_screen"):
            self._clean_previous_game()
        self.game = MineMadnessGame(name="game_screen")
        self.game.level = data["level"]

        if self.game.level > 1:
            Player.data = [globals()[key](attributes_dict=data["players_alive"][key])
                                   for key in data["players_alive"].keys()]
            Player.dead_data = [globals()[key](attributes_dict=data["players_dead"][key])
                                   for key in data["players_dead"].keys()]
        self.ongoing_game = True
        self._setup_dungeon_screen(DungeonLayout(game=self.game,
                                                 blueprint = Blueprint(layout=data["blueprint"]["layout"]),
                                                 torches_dict = data["torches_dict"]))


    def _convert_all_digit_keys_to_int(self, dictionary: dict) -> dict:
        """
        Checks all keys of a dictionary (also nested) and converts them to int if they are str and digit
        :param dictionary: dictionary to convert
        :return: converted dictionary
        """
        new_dict = dict()
        for key, value in dictionary.items():
            new_key = int(key) if isinstance(key, str) and key.isdigit() else key
            new_dict[new_key] = self._convert_all_digit_keys_to_int(value) if isinstance(value, dict) else value

        return new_dict


    @staticmethod
    def on_music_on(app, music_on):
        if music_on:
            app.music.volume = 1
            app.music.play()
        else:
            app.music.stop()

    def trigger_game_over(self, message: str) -> None:
        """
        Triggers game over screen
        :param message: message to display on game over screen (reason why game over)
        :return: None
        """
        if not self.game_mode_normal:
            remove(self.saved_game_file)
            self.saved_game = False
        self.sm.transition.duration = 1.5
        self.game_over_message = message
        self.sm.current = "game_over"
        self.ongoing_game = False
        self.sm.transition.duration = 0.3


######################################################### START APP ###################################################


if __name__ == "__main__":
    MineMadnessApp().run()
