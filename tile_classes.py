from kivy.uix.button import Button  # type: ignore

# from kivy.animation import Animation
# from kivy.properties import Clock
# from kivy.graphics import Ellipse, Color

import crapgeon_utils as utils

# import character_classes as characters
import token_classes as tokens


class Tile(Button):

    def __init__(self, row, col, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.row: int = row
        self.col: int = col
        self.position: tuple = (row, col)
        self.kind: str = kind
        self.token: tokens.SolidToken = (
            None  # defined when is by DungeonLayout.place_tokens
        )
        self.second_token: tokens.CharacterToken = (
            None  # tiles can have up to 2 tokens (shovel + monster for instance).
        )
        self.dungeon = dungeon_instance  # need to pass the instance of the dungeon to call dungeon.move_token from the class

    def on_release(self):

        player = self.dungeon.game.active_character

        if self.has_token(("player", None)) and self.get_character() != player:

            self.dungeon.game.switch_character(self.get_character())

        elif self.has_token(("wall", None)):

            player.dig(self)

            self.dungeon.game.update_switch("character_done")

        elif self.has_token(("monster", None)):

            player.fight_on_tile(self)

            self.dungeon.game.update_switch("character_done")

        else:

            start_tile = self.dungeon.get_tile(player.position)

            if (
                start_tile.token.kind == "player"
                and start_tile.token.character == player
            ):
                start_tile.token.move_player(start_tile, self)

            else:
                start_tile.second_token.move_player(start_tile, self)

    def update_token(self, *args):

        self.token.pos = self.pos
        self.token.size = self.size

    def is_activable(self):

        player = self.dungeon.game.active_character

        path = self.dungeon.find_shortest_path(
            self.dungeon.get_tile(player.position), self, (player.blocked_by)
        )

        if self.has_token(("player", None)):

            if self.get_character() == player:
                return True
            if self.get_character().has_moved():
                return False
            return True

        if (
            self.has_token(("wall", None))
            and utils.are_nearby(self, player)
            and player.stats.remaining_moves >= player.stats.digging_moves
        ):

            if player.stats.shovels > 0 or "digging" in player.free_actions:
                return True
            return False

        if self.has_token(("monster", None)) and utils.are_nearby(self, player):

            if player.stats.weapons > 0 or "fighting" in player.free_actions:
                return True
            return False

        if path and len(path) <= player.stats.remaining_moves:
            return True

        return False

    def has_token(self, token: tuple[str]) -> bool:

        if self.second_token and self.second_token.kind == token[0]:
            if token[1] is None or self.second_token.species == token[1]:
                return True
            else:
                return False

        if self.token and self.token.kind == token[0]:
            if token[1] is None or self.token.species == token[1]:
                return True
            else:
                return False

        return False

    def clear_token(self, token_kind):

        if self.second_token and self.second_token.kind == token_kind:
            self.dungeon.canvas.remove(self.second_token.shape)
            self.second_token = None

        elif self.token and self.token.kind == token_kind:
            self.dungeon.canvas.remove(self.token.shape)
            self.token = None

    def get_character(self):

        if self.second_token:
            return self.second_token.character
        else:
            return self.token.character
