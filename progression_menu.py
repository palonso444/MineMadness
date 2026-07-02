from __future__ import annotations

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from player_class import Player
from widget_classes import GameButton, GameLabel

class DowngradeButton(GameButton):
    """
    Class defining the buttons that downgrade stats
    """
    progr_menu = ObjectProperty(None)
    stat_name = StringProperty(None)

    def is_disabled(self) -> bool:
        # disabled if player is not alive or the real player upgrade level is equal than the temp upgrade_level (stat was not upgraded)
        player = self.progr_menu.player
        return not player.is_alive or (player.stats.upgrade_track[self.stat_name] ==
                self.progr_menu.players_temp_stats[player.species]["upgrade_track"][self.stat_name])

    def downgrade(self) -> None:
        """
        Downgrades the stat value, updates the temporary player.upgrade_track and reverts cost
        :return: None
        """
        temp_stats: dict = self.progr_menu.players_temp_stats[self.progr_menu.player.species]
        if type(temp_stats[self.stat_name]) is int:
            temp_stats[self.stat_name] -= Player.upgrade_interval_int
        elif type(temp_stats[self.stat_name]) is float:
            temp_stats[self.stat_name] -= Player.upgrade_interval_float
        else:
            raise TypeError(f"Invalid stat type: {type(temp_stats[self.stat_name])}")

        temp_stats["upgrade_track"][self.stat_name] -= 1
        next_level: int = temp_stats["upgrade_track"][self.stat_name] + 1
        # revert cost
        self.progr_menu.group_xp += self.progr_menu.player.get_upgrade_cost(self.stat_name, next_level)


class UpgradeButton(GameButton):
    """
    Class defining the buttons that upgrade stats
    """
    progr_menu = ObjectProperty(None)
    stat_name = StringProperty(None)

    def is_disabled(self) -> bool:
        # disabled if player is not alive or the cost of upgrade is higher than the available group_xp
        next_level: int = self.progr_menu.players_temp_stats[self.progr_menu.player.species]["upgrade_track"][self.stat_name] + 1
        player = self.progr_menu.player
        return not player.is_alive or self.progr_menu.player.get_upgrade_cost(self.stat_name, next_level) > self.progr_menu.group_xp

    def upgrade(self) -> None:
        """
        Upgrades the stat value, updates the temporary player.upgrade_track and applies xp cost
        :return: None
        """
        temp_stats: dict = self.progr_menu.players_temp_stats[self.progr_menu.player.species]
        next_level: int = temp_stats["upgrade_track"][self.stat_name] + 1
        if type(temp_stats[self.stat_name]) is int:
            temp_stats[self.stat_name] += Player.upgrade_interval_int
        elif type(temp_stats[self.stat_name]) is float:
            temp_stats[self.stat_name] += Player.upgrade_interval_float
        else:
            raise TypeError(f"Invalid stat type: {type(temp_stats[self.stat_name])}")

        temp_stats["upgrade_track"][self.stat_name] += 1
        self.progr_menu.group_xp -= self.progr_menu.player.get_upgrade_cost(self.stat_name, next_level)


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

class NextLevelButton(GameButton):
    """
    Class defining the button leading to the next level
    """
    progr_menu = ObjectProperty(None)

    def trigger_next_level(self) -> None:
        """
        Transfers the temp_stats to real stats and starts_next_level()
        """
        Player.group_xp = self.progr_menu.group_xp
        self.set_players_stats()
        self.progr_menu.reset_properties()
        App.get_running_app().start_next_level()

    def set_players_stats(self) -> None:
        """
        Overwrites players stats to match the temp_stats
        """
        for player in Player.data:
            for stat in self.progr_menu.players_temp_stats[player.species].keys():
                setattr(player.stats, stat, self.progr_menu.players_temp_stats[player.species][stat])


class CharacterProgressionMenu(Screen):
    background = ObjectProperty(None, allownone=True)
    player = ObjectProperty(None, allownone=True)

    # DISPLAY PROPERTIES.
    # Stats displayed are temp_stats
    group_xp = NumericProperty(None, allownone=True)
    player_name = StringProperty(None, allownone=True)
    player_strength = NumericProperty(None, allownone=True)
    player_health = NumericProperty(None, allownone=True)
    player_percent_critical = NumericProperty(None, allownone=True)
    player_moves = NumericProperty(None, allownone=True)
    player_recovery = NumericProperty(None, allownone=True)
    player_trap_spotting_chance = NumericProperty(None, allownone=True)

    # UPGRADE COST PROPERTIES
    upgrade_cost_strength = NumericProperty(None, allownone=True)
    upgrade_cost_health = NumericProperty(None, allownone=True)
    upgrade_cost_moves = NumericProperty(None, allownone=True)
    upgrade_cost_percent_critical = NumericProperty(None, allownone=True)
    upgrade_cost_recovery = NumericProperty(None, allownone=True)
    upgrade_cost_trap_spotting_chance = NumericProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.players_temp_stats: dict[str, dict] = {}

    def on_pre_enter(self, *args) -> None:
        """
        Triggered before screen transition starts. Sets the initial conditions of the menu
        :return: None
        """
        self.get_temp_stats()
        self.group_xp = Player.group_xp
        # sawyer is always the first character to show up
        self.player = Player.data[0]

    @staticmethod
    def on_group_xp(instance: CharacterProgressionMenu, value: int) -> None:
        """
        Enables or disables the upgrade and downgrade buttons and displays new stats
        :return: None
        """
        if instance.player is not None:
            for button_id in instance.ids.keys():
                if button_id.startswith("downgrade_button") or button_id.startswith("upgrade_button"):
                    instance.ids[button_id].disabled = instance.ids[button_id].is_disabled()
            instance.display_stats()

    @staticmethod
    def on_player(instance: CharacterProgressionMenu, player: Player) -> None:
        """
        Triggers the changes in the menu upon switching player (name and displayed stats)
        :param instance: instance of the CharacterProgressionMenu
        :param player: new player to show
        :return: None
        """
        if player is not None:
            instance.display_player_name()
            instance.display_stats()

    def get_temp_stats(self) -> None:
        """
        Gets the current stats of all players to display them in the menu
        :return: None
        """
        for player in Player.data:
            self.players_temp_stats[player.species] = player.stats.to_dict()
            self.players_temp_stats[player.species]["upgrade_track"] = (
                self.players_temp_stats[player.species]["upgrade_track"].copy())

    def set_previous_player(self) -> None:
        """
        Sets the previous player in player order
        :return: None
        """
        idx: int = self._get_current_player_index()
        if idx == 0:
            self.player = Player.data[-1]
        else:
            self.player = Player.data[idx-1]

    def set_next_player(self) -> None:
        """
        Sets next player in player order
        :return: None
        """
        idx: int = self._get_current_player_index()

        if idx == len(Player.data) - 1:
            self.player = Player.data[0]
        else:
            self.player = Player.data[idx+1]

    def display_stats(self) -> None:
        """
        Displays the stats and their upgrade costs of the selected player
        :return: None
        """
        self.player_strength = self.players_temp_stats[self.player.species]["natural_strength"]
        self.player_health = self.players_temp_stats[self.player.species]["natural_health"]
        self.player_percent_critical = self.players_temp_stats[self.player.species]["percent_critical"]
        self.player_moves = self.players_temp_stats[self.player.species]["natural_moves"]
        self.player_recovery = self.players_temp_stats[self.player.species]["recovery"]
        self.player_trap_spotting_chance = self.players_temp_stats[self.player.species]["trap_spotting_chance"]

        upgrade_track: dict = self.players_temp_stats[self.player.species]["upgrade_track"]
        self.upgrade_cost_strength = self.player.get_upgrade_cost("natural_strength", upgrade_track["natural_strength"] + 1)
        self.upgrade_cost_health = self.player.get_upgrade_cost("natural_health", upgrade_track["natural_health"] + 1)
        self.upgrade_cost_moves = self.player.get_upgrade_cost("natural_moves", upgrade_track["natural_moves"] + 1)
        self.upgrade_cost_percent_critical = self.player.get_upgrade_cost("percent_critical", upgrade_track["percent_critical"] + 1)
        self.upgrade_cost_recovery = self.player.get_upgrade_cost("recovery", upgrade_track["recovery"] + 1)
        self.upgrade_cost_trap_spotting_chance = self.player.get_upgrade_cost("trap_spotting_chance", upgrade_track["trap_spotting_chance"] + 1)

    def display_player_name(self) -> None:
        """
        Displays the name of the player and informs whether is dead or not
        :return: None
        """
        if self.player.is_alive:
            self.player_name =  self.player.name
        else:
            self.player_name =  f"{ self.player.name} (dead)"

    def _get_current_player_index(self) -> int:
        """
        Gets the index (in Player.data) of the current displayed player
        :return: the index
        """
        return Player.data.index(self.player)

    def reset_properties(self) -> None:
        """
        Resets all properties
        """
        # background is not reset to avoid weird flash in the background
        # self.background = None
        self.player = None
        self.group_xp = None
        self.player_name = None
        self.player_strength = None
        self.player_health = None
        self.player_percent_critical = None
        self.player_moves = None
        self.player_recovery = None
        self. player_trap_spotting_chance = None
        self.upgrade_cost_strength = None
        self.upgrade_cost_health = None
        self.upgrade_cost_moves = None
        self.upgrade_cost_percent_critical = None
        self.upgrade_cost_recovery = None
        self.upgrade_cost_trap_spotting_chance = None
