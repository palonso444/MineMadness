from __future__ import annotations
from kivy.app import App
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

import player_classes as players
import monster_classes as monsters
from interface import Interfacebutton
from player_classes import Player
from tokens_fading import DamageToken


class MainMenu(Screen):
    pass

class HowToPlay(Screen):
    pass

class OutGameOptions(Screen):
    pass

class InGameOptions(Screen):
    pass

class NewGameConfig(Screen):
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

    # INTERFACE LABELS PROPERTIES
    # callbacks are defined in the kv file
    shovels = BooleanProperty(None)
    weapons = BooleanProperty(None)
    gems = BooleanProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level: int = 1
        self.active_character: Character | None = None  # defined by MineMadnessGame.on_active_character_id()
        self.total_gems: int | None = None  # defined by MineMadnessGame.DungeonLayout.on_pos()
        self.ability_button_active: bool | None = None  # activated and deactivates button (no effect if pressed)
        self.game_already_over: bool = False  # to avoid interferences of game_over screens if massive killing

    @staticmethod
    def on_dungeon(game: MineMadnessGame, dungeon: DungeonLayout) -> None:
        """
        Triggered when dungeon is ready and assigned to MineMadnessGame.dungeon attribute.
        :param game: instance of MineMadnessGame
        :param dungeon: assigned dungeon instance
        :return: None
        """
        game.total_gems = game.dungeon.stats.gem_number  # self.game defined in kv file
        players.Player.gems = 0
        game.check_if_game_over(game=game)
        if not game.game_already_over:
            players.Player.set_starting_player_order()
            for player in players.Player.data:
                player.remove_all_effects()  # 0 is the default turn argument
            players.Player.exited.clear()

            App.get_running_app().save_game()
            App.get_running_app().level = game.level

            game.initialize_switches()  # this starts the game

    def initialize_switches(self) -> None:
        self.turn = 0  # even for players, odd for monsters. Player starts

        self.shovels = False
        self.weapons = False
        self.gems = False

        self.ability_button_active = True  # TODO: when button unbinding in self.on_ability_button() works this has to go

    def update_interface(self) -> None:
        """
        Updates the interface display
        :return: None
        """
        for button_type in Interfacebutton.types:
            self.inv_object = button_type

        self.ids.level_label.text = "Depth: " + str(self.level * 30) + " ft." \
            if self.active_character.kind == "player" else ""

        self.update_switch("shovels")
        self.update_switch("weapons")
        self.update_switch("gems")
        self.update_switch("ability_button")

        self.ids.jerky_button.text = "Jerky" if self.active_character.kind == "player" else ""
        self.ids.coffee_button.text = "Coffee" if self.active_character.kind == "player" else ""
        self.ids.tobacco_button.text = "Tobacco" if self.active_character.kind == "player" else ""
        self.ids.whisky_button.text = "Whisky" if self.active_character.kind == "player" else ""
        self.ids.talisman_button.text = "Talisman" if self.active_character.kind == "player" else ""

        self.update_experience_bar()

    def update_switch(self, switch_name) -> None:
        """
        Updates the value of a switch (Property) to activate it
        :param switch_name: switch to activate
        :return: None
        """
        switch_value = getattr(self, switch_name)
        if isinstance(switch_value, bool):
            switch_value = not switch_value
        elif switch_name == "turn":
            switch_value += 1
        elif switch_name == "active_character_id":
            switch_value = self.active_character_id
            setattr(self, switch_name, None)

        setattr(self, switch_name, switch_value)

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

    @staticmethod
    def on_character_done(game: MineMadnessGame, value: bool) -> None:
        """
        Checks what to do when a character finishes a movement, but it may still have movements left
        :param game: current instance of MineMadnessGame
        :param value: current boolean value of the switch
        :return: None
        """
        game.check_if_all_players_exited()
        # call game.check_if_game_over() if game over for lack of shovels is implemented

        if game.turn is not None:

            if monsters.Monster.all_dead_or_out() and game.active_character.stats.remaining_moves == 0:
                game.active_character.stats.remaining_moves = game.active_character.stats.moves
                game.active_character.remove_effects_if_over(game.turn)
                if game.active_character.token is not None:  # dead characters have no Token
                    game.active_character.token.unselect_token()
                game.update_switch("turn")

            elif game.active_character.stats.remaining_moves > 0:
                if game.active_character.kind == "player":
                    game.activate_accessible_tiles(game.active_character.stats.remaining_moves)
                elif game.active_character.kind == "monster":
                    if game.active_character.has_acted:
                        game.active_character.acted_on_tile = False
                        game.active_character.move()
                    else:
                        game.next_character()

            else:
                if game.active_character.kind == "player":
                    game.active_character.remove_effects_if_over(game.turn)
                    if game.active_character.token is not None:  # dead characters have no Token
                        game.active_character.token.unselect_token()
                game.next_character()

    @staticmethod
    def on_turn(game: MineMadnessGame, turn: int | None) -> None:
        """
        On new turn, resets movements of the characters (monsters or players). Sets self.active_character_id to 0
        and updates it if the value was already 0 (there is only one character left)
        :param game: current instance of MineMadnessGame
        :param turn: turn number (even for players, odd for monsters)
        :return: None
        """
        if turn is not None:
            if turn % 2 == 0 or monsters.Monster.all_dead_or_out():
                players.Player.initialize_moves_attacks()
            else:
                monsters.Monster.initialize_moves_attacks()

            if game.active_character_id == 0:
                game.update_switch("active_character_id")
            else:
                game.active_character_id = 0

    @staticmethod
    def on_active_character_id(game: MineMadnessGame, character_id: int | None) -> None:
        """
        Checks what to do when the active character changes.
        :param game: current instance of MineMadnessGame
        :param character_id: id of the new active character
        :return: None
        """
        # restores any color modifications from previous Characters (e.g. by hiding)
        game.dungeon.restore_canvas_color("canvas")
        game.dungeon.restore_canvas_color("after")

        if character_id is not None and not Player.all_dead_or_out():
            # if player turn or no monsters
            if game.turn % 2 == 0 or monsters.Monster.all_dead_or_out():
                game.active_character = players.Player.data[character_id]

                if game.active_character.has_moved and not monsters.Monster.all_dead_or_out():
                    game.next_character()

                else:
                    game.active_character.token.select_character()
                    game.update_interface()
                    game.activate_accessible_tiles(game.active_character.stats.remaining_moves)

            else:  # if monsters turn and monsters in the game
                game.dungeon.disable_all_tiles()  # tiles deactivated in monster turn
                game.active_character = monsters.Monster.data[game.active_character_id]
                game.update_interface()
                game.active_character.token.select_character()
                game.active_character.move()

    @staticmethod
    def on_player_exited(game: MineMadnessGame, value: bool) -> None:
        """
        Handles the change of level or turn when the active character exits the level
        :param game: current instance of MineMadnessGame
        :param value: current boolean value of the switch
        :return: None
        """
        if players.Player.all_dead_or_out():
            game.finish_level()
        elif game.active_character_id == len(players.Player.data):
            game.update_switch("turn")
        else:
            game.update_switch("active_character_id")

    def next_character(self) -> None:
        if self.active_character.id < len(self.active_character.__class__.data) - 1:
            self.active_character_id += 1  # next character on list moves

        else:  # if end of characters list reached (all have moved)
            self.update_switch("turn")

    def activate_accessible_tiles(self, steps: int) -> None:
        """
        Gets the total range of activable tiles (player movement range and other player positions if player.
        did not move if monsters are present, otherwise all other players positions).
        :param steps: number of steps within which accessible Tiles must be activated
        :return: None
        """

        if monsters.Monster.all_dead_or_out():
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

    def switch_character(self, new_active_character: Character) -> None:
        """
        Changes the active character (self.active_character).
        :param new_active_character: character to be activated.
        :return: None
        """
        players.Player.swap_characters(new_active_character.id, self.active_character.id)

        self.active_character.token.unselect_token()
        self.active_character = new_active_character
        self.update_switch("active_character_id")

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
        if players.Player.all_dead_or_out() and not players.Player.all_players_dead() and not self.game_already_over:
            self.turn = None  # needed to abort of MineMadnessGame.on_character_done()
            self.finish_level()

    @staticmethod
    def check_if_game_over(animation: Animation | None = None,
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

        if players.Player.all_players_dead():
            game.game_already_over = True
            game.turn = None  # needed to abort of MineMadnessGame.on_character_done()
            App.get_running_app().trigger_game_over("Monsters killed y'all!")

        elif (Player.check_if_dead("sawyer") and Player.gems < game.total_gems
            and not any(player.has_item("talisman") for player in Player.data)):
            game.game_already_over = True
            game.turn = None  # needed to abort of MineMadnessGame.on_character_done()
            App.get_running_app().trigger_game_over("Only Sawyer could pick up gems...")

    def finish_level(self) -> None:
        """
        Finishes the level and notified MineMadnessApp to provide a new level
        :return: None
        """
        monsters.Monster.data.clear()
        self.dungeon.unschedule_all_events()
        self.level += 1
        App.get_running_app().remove_dungeon_from_game()
        App.get_running_app().add_dungeon_to_game()
        self.turn = None  # needed to abort of MineMadnessGame.on_character_done()
