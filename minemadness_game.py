from __future__ import annotations

from kivy.app import App
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.screenmanager import Screen

from player_classes import Player
from character_class import Character
from monster_classes import Monster
from dungeon_classes import DungeonLayout


class MineMadnessGame(Screen):  # initialized in kv file

    level = NumericProperty(None)
    dungeon = ObjectProperty(None, allownone=True)
    turn = NumericProperty(None, allownone=True)
    active_character = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level: int = 1
        self.advanced_start: bool = False  # for testing, set to True and change level attribute
        self.ability_button_active: bool | None = None  # activated and deactivates button (no effect if pressed)

        self.bind(dungeon=self.start_level)

    @staticmethod
    def start_level(game: MineMadnessGame, dungeon: DungeonLayout) -> None:
        """
        Triggered when dungeon assigned to self.dungeon. Sets up Class attributes of Characters and starts new level
        :param game: instance of MineMadnessGame
        :param dungeon: assigned dungeon instance
        :return: None
        """
        if dungeon is not None:
            dungeon.build_level()
            if game.level == 1 or game.advanced_start:
                Player.set_player_order()
            Player.gems = 0
            App.get_running_app().save_game()
            game.ability_button_active = True
            game.turn = 0   # this starts the game

    def update_interface(self) -> None:
        """
        Updates the interface display. Updating of labels and enabling / disabling buttons goes differently. Update
        interface functions enable and disable buttons. Update label updates the text of the button or erases it
        :return: None
        """
        self.update_label("name_label", self.active_character.name.upper())
        self.update_experience_bar()
        self.update_inventory_interface()
        self.update_lower_interface()

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
            # lower interface
            self.update_label("options_button", "Options")
            self.update_label("main_menu_button", "Main Menu")

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
            # lower interface
            self.update_label("options_button", None)
            self.update_label("main_menu_button", None)

        self.update_ability_button()

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

    def update_inventory_button(self, item: str, item_value: int) -> None:
        """
        When a character picks up an object enables the corresponding button if applicable.
        :param item: item to update
        :param item_value: new value of the item
        :return: None
        """
        self.ids[item + "_button"].disabled = True if item_value == 0 else False

    def update_inventory_interface(self) -> None:
        """
        Updates the whole inventory interface
        :return: None
        """
        for item, value in self.active_character.inventory.items():
            self.update_inventory_button(item, value)

    def update_lower_interface(self) -> None:
        """
        Updates the interface showed at the bottom of the game screen
        :return: None
        """
        self.ids.options_button.disabled = False if self.turn % 2 == 0 else True
        self.ids.main_menu_button.disabled = False if self.turn % 2 == 0 else True

    def update_ability_button(self) -> None:
        """
        Updates the display of the ability button
        :return: None
        """
        self.ability_button_active = False

        if self.active_character.kind == "monster":
            self.ids.ability_button.text = ""
            self.ids.ability_button.disabled = True
            self.ids.ability_button.state = "normal"

        elif self.active_character.kind == "player":
            self.ids.ability_button.text = self.active_character.ability_display
            self.ids.ability_button.disabled = not self.ids.ability_button.condition_active
            self.ids.ability_button.state = "down" if self.active_character.ability_active else "normal"

        self.ability_button_active = True

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
        Player.data.clear()
        Monster.data.clear()
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
        if turn is not None and not game.finish_game_or_finish_level():
            # monsters all dead and players starts turn with other than Sawyer
            if game.active_character is not None:
                Player.reset_moves()
                c = game.active_character
                game.active_character = None  # to ensure updating
                game.active_character = c
            else:
                if turn % 2 == 0 or Monster.all_dead():
                    Player.reset_moves()
                    game.active_character = next(player for player in Player.data if player.state == "in_game")
                else:
                    Monster.reset_moves()
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
                # initialize moves here so on_turn() knows turn must start with this character
                character.remaining_moves = character.stats.moves
                game.turn += 1

            # player turn
            elif game.turn % 2 == 0 or Monster.all_dead():
                character.token.select_character()
                game.update_interface()
                game.activate_accessible_tiles(game.active_character.remaining_moves)

            # monsters turn
            else:
                game.dungeon.disable_all_tiles()  # tiles deactivated in monster turn
                game.update_interface()
                character.token.select_character()
                character.move()

    def character_moved(self) -> None:
        """
        Checks what to do when a character finishes a movement, but it may still have movements left
        :return: None
        """
        if self.turn is not None:

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
                if self._check_if_game_over() is None and not (Player.all_out() and not Player.all_dead()):
                    self.activate_next_character()

    def activate_next_character(self, start_index_mod: int = 0) -> None:
        """
        Activates next active character or switch turn if all characters have been already activated
        :start_index_mod: modifier of the index where starting the search of next character
        :return: None
        """
        act_char_cls = self.active_character.__class__

        if any(character.state == "in_game" and character.has_moves_left for character in act_char_cls.data):
            start_index: int = act_char_cls.data.index(self.active_character) + start_index_mod
            self.active_character: Character = act_char_cls.get_next_in_game_with_moves(starting_index=start_index)
        else:
            self.active_character = None
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

    def _check_if_game_over(self) -> str | None:
        """
        Checks if the game is over and returns the game over message in case game is over
        :return: The game over message, None if the game is not over
        """
        if Player.all_dead():
            return "Monsters killed y'all!"

        if (Player.check_if_dead("sawyer") and Player.gems < self.dungeon.total_gems
            and not any(player.has_item("talisman") for player in Player.get_all_with_state("is_alive"))):
            return "Only Sawyer could pick up gems..."

        return None

    def finish_game_or_finish_level(self) -> bool:
        """
        Checks if the game is over, and if yes, triggers game over screen. If not but no players in game, triggers next level
        :return: True if game or level are is finished, False if ir continues
        """
        game_over_msg : str | None = self._check_if_game_over()

        if game_over_msg is not None:
            self.turn = None
            App.get_running_app().trigger_game_over(game_over_msg)
            return True
        if Player.all_out() and not Player.all_dead():
            self.finish_level()
            return True
        return False

    def finish_level(self) -> None:
        """
        Finishes the level and provides a new one
        :return: None
        """
        Monster.data.clear()
        self.dungeon.unschedule_all_events()
        self.active_character = None
        self.turn = None
        self.level += 1
        self.remove_dungeon_from_game()
        self.add_dungeon_to_game()
