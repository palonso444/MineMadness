from __future__ import annotations
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from player_class import Player
from widget_classes import GameButton


class SwitchPlayerButton(GameButton):
    """
    Class defining the Buttons used to switch character. Upon release, they trigger the corresponding method
    of the CharacterProgressionMenu class.
    """
    button_type = StringProperty(None)
    progr_menu = ObjectProperty(None)

    def on_release(self, *args) -> None:
        if self.button_type == "previous":
            self.progr_menu.set_previous_player()
        elif self.button_type == "next":
            self.progr_menu.set_next_player()
        else:
            raise ValueError(f"Invalid button_type: '{self.button_type}'. Valid are 'next' or 'previous'")

class CharacterProgressionMenu(Screen):
    background = ObjectProperty(None, allownone=True)
    player_species = StringProperty(None)
    player_name = StringProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.players_temp_stats: dict[str, dict] = {}

    def on_pre_enter(self, *args) -> None:
        """
        Triggered before screen transition starts. Sets the initial conditions of the menu
        :return: None
        """
        # sawyer is always the first character to show
        self.player_species = "sawyer"
        self.get_stats()

    @staticmethod
    def on_player_species(instance: Screen, player_species: str) -> None:
        """
        Triggers the changes in the menu upon switching player (name and displayed stats)
        :param instance: instance of the CharacterProgressionMenu
        :param player_species: species of the new player to show
        :return: None
        """
        instance.player_name = Player.get_by_species(player_species).name

    def get_stats(self) -> None:
        """
        Gets the current stats of all players to display them in the menu
        :return: None
        """
        for player in Player.data:
            self.players_temp_stats[player.species] = player.stats.to_dict()

    def set_previous_player(self) -> None:
        """
        Sets the previous player in player order
        :return: None
        """
        idx: int = self._get_current_player_index()
        if idx == 0:
            self.player_species = Player.data[-1].species
        else:
            self.player_species = Player.data[idx-1].species

    def set_next_player(self) -> None:
        """
        Sets next player in player order
        :return: None
        """
        idx: int = self._get_current_player_index()
        if idx == len(Player.data) - 1:
            self.player_species = Player.data[0].species
        else:
            self.player_species = Player.data[idx+1].species

    def _get_current_player_index(self) -> int:
        """
        Gets the index (in Player.data) of the current displayed player
        :return: the index
        """
        return Player.data.index(Player.get_by_species(self.player_species))
