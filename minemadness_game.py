from __future__ import annotations

from typing import Optional

from kivy.app import App
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

import player_classes as players
import monster_classes as monsters
from character_class import Character
from interface import Interfacebutton
from monster_classes import Monster
from player_classes import Player
from tokens_fading import DamageToken
from dungeon_classes import DungeonLayout


class MineMadnessGame(Screen):  # initialized in kv file

    level = NumericProperty(None)
    dungeon = ObjectProperty(None)
    turn = NumericProperty(None, allownone=True)
    active_character = ObjectProperty(None, allownone=True)

    ability_button = BooleanProperty(False)

    inv_object = StringProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level: int = 1
        self.advanced_start: bool = False  # for testing, set to True and change level attribute
        self.ability_button_active: bool | None = None  # activated and deactivates button (no effect if pressed)
        self.game_already_over: bool = False  # to avoid interferences of game_over screens if massive killing

        self.bind(dungeon=self.start_level)

    @staticmethod
    def start_level(game: MineMadnessGame, dungeon: DungeonLayout) -> None:
        """
        Triggered when dungeon assigned to self.dungeon. Triggers the setup of the level
        :param game: instance of MineMadnessGame
        :param dungeon: assigned dungeon instance
        :return: None
        """
        if dungeon is not None:

            #if not game.game_already_over:
                #game.finish_game_if_over(game=game)  # TODO: this must be out of here

            dungeon.set_tiles()
            dungeon.match_blueprint()
            dungeon.place_torches(size_modifier=0.5)

            players.Player.gems = 0
            if game.level == 1 or game.advanced_start:
                players.Player.set_player_order()
            else:
                for player in players.Player.data:
                    if player.state == "in_game":
                        player.remove_all_effects()

            App.get_running_app().save_game()
            game.initialize_switches()  # this starts the game

    def initialize_switches(self) -> None:
        self.turn = 0  # even for players, odd for monsters. Player starts
        self.ability_button_active = True  # TODO: when button unbinding in self.on_ability_button() works this has to go

    def update_interface(self) -> None:
        """
        Updates the interface display
        :return: None
        """
        for button_type in Interfacebutton.types:
            self.inv_object = button_type

        self.update_label("name_label", self.active_character.name.upper())
        self.update_experience_bar()

        if self.active_character.kind == "player":
            self.update_label("level_label", self.level * 30)
            self.update_label("shovels_label", self.active_character.shovels)
            self.update_label("weapons_label", self.active_character.weapons)
            self.update_label("gems_label", Player.gems)
            self.update_label("jerky_button", "Jerky")
            self.update_label("coffee_button", "Coffee")
            self.update_label("tobacco_button", "Tobacco")
            self.update_label("whisky_button", "Whisky")
            self.update_label("talisman_button", "Talisman")
        else:
            self.update_label("level_label", None)
            self.update_label("shovels_label", None)
            self.update_label("weapons_label", None)
            self.update_label("gems_label", None)
            self.update_label("jerky_button", None)
            self.update_label("coffee_button", None)
            self.update_label("tobacco_button", None)
            self.update_label("whisky_button", None)
            self.update_label("talisman_button", None)

        self.force_update("ability_button")

    def force_update(self, switch_name) -> None:
        """
        Forces updating a property value even if the value does not change
        :param switch_name: property name to force update
        :return: None
        """
        switch_value = getattr(self, switch_name)
        if isinstance(switch_value, bool):
            switch_value = not switch_value
        elif switch_name == "turn":
            raise NotImplementedError("Deprecated! Use self.turn += 1 instead")

        setattr(self, switch_name, switch_value)

    def update_label(self, label_id: str, value: int | str | None) -> None:
        """
        Updates an interface label
        :param label_id: id of the label
        :param value: value to update
        :returns: None
        """
        if value is not None:
            if label_id.endswith("button"):
                self.ids[label_id].text = value
            elif label_id == "level_label":
                self.ids[label_id].text = f"Depth: {value} ft."
            elif label_id == "name_label":
                self.ids[label_id].text = value
            elif label_id == "gems_label":
                self.ids[label_id].text = f"Gems: {value}/{self.dungeon.total_gems}"
            else:
                self.ids[label_id].text = f"{label_id.split('_')[0].capitalize()}: {value}"
        else:
            self.ids[label_id].text = ""

    def update_experience_bar(self) -> None:
        """
        Updates the range of the experience bar according to the current active character.
        :return: None
        """
        if self.active_character.kind == "player":
            self.ids.experience_bar.max = self.active_character.stats.exp_to_next_level
            self.ids.experience_bar.value = self.active_character.experience
        else:
            self.ids.experience_bar.value = 0

    @staticmethod
    def on_ability_button(game: MineMadnessGame, value: bool) -> None:
        """
        Updates the state of the ability button depending on the circumstances of the game
        :param game: current instance of MineMadnessGame
        :param value: current boolean value of the switch
        :return: None
        """
        game.ability_button_active = False

        if game.active_character.kind == "monster":
            game.ids.ability_button.text = ""
            game.ids.ability_button.disabled = True
            game.ids.ability_button.state = "normal"

        elif game.active_character.kind == "player":
            game.ids.ability_button.text = game.active_character.ability_display
            game.ids.ability_button.disabled = not game.ids.ability_button.condition_active
            game.ids.ability_button.state = "down" if game.active_character.ability_active else "normal"

        game.ability_button_active = True

    def add_dungeon_to_game(self, dungeon: DungeonLayout | None = None) -> None:
        """
        Adds a dungeon to the game
        :param dungeon: DungeonLayout to add. If None, a random one according to MineMadnessApp.game.level is generated
        :return: None
        """
        scrollview = self.children[0].children[1]
        if dungeon is None:
            dungeon = DungeonLayout(game=self)
        self.dungeon = dungeon
        scrollview.add_widget(dungeon)

    def remove_dungeon_from_game(self) -> None:
        """
        Removes the dungeon from the game
        :return: None
        """
        scrollview = self.children[0].children[1]
        scrollview.remove_widget(self.dungeon)
        self.dungeon = None

    def clean_previous_game(self) -> None:
        """
        Cleans the data from the previous game
        :return: None
        """
        players.Player.data.clear()
        monsters.Monster.data.clear()
        self.dungeon.unschedule_all_events()

    ####### THE FOLLOWING GROUP OF FUNCTIONS MANAGE THE TURN SEQUENCE  ###########

    @staticmethod
    def on_turn(game: MineMadnessGame, turn: int | None) -> None:
        """
        Resets movements of the characters (monsters or players) and sets the active_character to
        the first Character with state in_game
        :param game: current instance of MineMadnessGame
        :param turn: turn number (even for players, odd for monsters)
        :return: None
        """
        if turn is not None:
            game.active_character = None  # to ensure updating
            if turn % 2 == 0 or monsters.Monster.all_dead():
                players.Player.initialize_moves_attacks()
                game.active_character = next(player for player in Player.data if player.state == "in_game")
            else:
                monsters.Monster.initialize_moves_attacks()
                game.active_character = next(monster for monster in Monster.data if monster.state == "in_game")

    @staticmethod
    def on_active_character(game: MineMadnessGame, character: Character | None) -> None:
        """
        Checks what to do when the active character changes
        :param game: current instance of MineMadnessGame
        :param character: new active character
        :return: None
        """
        if character is not None:
            # restores any color modifications from previous Characters (e.g. by hiding)
            game.dungeon.restore_canvas_color("canvas")
            game.dungeon.restore_canvas_color("after")

            # if no monsters and character is selected again after moves run out, a turn passes
            if Monster.all_dead() and not character.has_moves_left:
                game.turn += 1

            # player turn
            elif game.turn % 2 == 0 or monsters.Monster.all_dead():
                game.active_character.token.select_character()
                game.update_interface()
                game.activate_accessible_tiles(game.active_character.remaining_moves)

            # monsters turn
            else:
                game.dungeon.disable_all_tiles()  # tiles deactivated in monster turn
                game.update_interface()
                game.active_character.token.select_character()
                game.active_character.move()

    def character_moved(self) -> None:
        """
        Checks what to do when a character finishes a movement, but it may still have movements left
        :return: None
        """
        if self.turn is not None:
            #self.check_if_all_players_exited()
            # call game.check_if_game_over() if game over for lack of shovels is implemented

            # turn continues
            if self.active_character.has_moves_left:
                if self.active_character.kind == "player":
                    self.activate_accessible_tiles(self.active_character.remaining_moves)
                elif self.active_character.kind == "monster":
                    if self.active_character.has_acted:
                        self.active_character.acted_on_tile = False
                        self.active_character.move()
                    else:
                        self.activate_next_character()

            # end turn
            else:
                if self.active_character.kind == "player":
                    self.active_character.remove_effects_if_over(self.turn)
                    if self.active_character.token is not None:  # dead characters have no Token
                        self.active_character.token.unselect_token()
                self.activate_next_character()

    def activate_next_character(self, start_index_mod: int = 0) -> None:
        """
        Activates next active character or switch turn if all characters have been already activated
        :start_index_mod: modifier of the index where starting the search of next character
        :return: None
        """
        act_char_cls = self.active_character.__class__

        # characters can move until they have no moves left.
        # Monsters move only once (remaining_moves = 0 when finish first move)
        if any(character.has_moves_left and character.state == "in_game" for character in act_char_cls.data):
            start_index: int = act_char_cls.data.index(self.active_character) + start_index_mod
            self.active_character: Character = act_char_cls.find_next_char_in_game_with_moves(starting_index=start_index)
        else:
            self.turn += 1

    ####### END OF FUNCTIONS MANAGING THE TURN SEQUENCE  ##################

    def activate_accessible_tiles(self, steps: int) -> None:
        """
        Gets the total range of activable tiles (player movement range and other player positions) and calls the
        activation check for all of them
        :param steps: number of steps within which accessible Tiles must be activated
        :return: None
        """
        self.dungeon.disable_all_tiles()
        player_movement_range = self.dungeon.get_range(self.active_character.get_position(), steps)
        positions_in_range = player_movement_range.union({player.get_position() for player in Player.data if player.state == "in_game"})
        self.dungeon.enable_tiles(positions_in_range, self.active_character)

    def switch_character(self, new_active_character: Character) -> None:
        """
        Changes the active character (self.active_character).
        :param new_active_character: character to be activated.
        :return: None
        """
        self.active_character.token.unselect_token()
        self.active_character = new_active_character

    @staticmethod
    def on_inv_object(game: MineMadnessGame, inv_object: str | None) -> None:
        """
        When a character picks up an object enables the corresponding button if applicable.
        :param game: current instance of the game.
        :param inv_object: object of the inventory just picked up
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

    def check_if_all_players_exited(self) -> None:
        """
        Checks if all Players have exited the level, so game must move to the next level
        :return: None
        """
        # players may not be all dead and game will be over (in case Sawyer is killed)
        if players.Player.all_out() and not players.Player.all_players_dead() and not self.game_already_over:
            #self.turn = None  # needed to abort of MineMadnessGame.on_character_done()
            self.finish_level()

    @staticmethod
    def finish_game_if_over(animation: Animation | None = None,
                            damage_token: DamageToken | None = None,
                            game: MineMadnessGame | None = None) -> None:
        """
        Checks if the game is over, and if yes, triggers game over screen. It is bound after fading out
        of DamageToken
        :param animation: animation object of the DamageToken
        :param damage_token: DamageToken instance
        :param game: this function can also be called manually (not as callback). In that case, game argument must be
        passed
        :return: None
        """
        if damage_token is not None:
            game = damage_token.game
        elif game is not None:
            game = game
        else:
            raise ValueError("Either game or damage_token must be not None")

        if players.Player.all_dead():
            game.game_already_over = True
            game.turn = None  # needed to abort of MineMadnessGame.on_character_done()
            App.get_running_app().trigger_game_over("Monsters killed y'all!")

        elif (Player.check_if_dead("sawyer") and Player.gems < game.dungeon.total_gems
            and not any(Player.get_data(player_id).has_item("talisman") for player_id in Player.in_game)):
            game.game_already_over = True
            game.turn = None  # needed to abort of MineMadnessGame.on_character_done()
            App.get_running_app().trigger_game_over("Only Sawyer could pick up gems...")

    def finish_level(self) -> None:
        """
        Finishes the level and provides a new one
        :return: None
        """
        monsters.Monster.data.clear()
        self.dungeon.unschedule_all_events()
        self.turn = None
        self.active_character = None
        self.level += 1
        self.remove_dungeon_from_game()
        self.add_dungeon_to_game()
