from __future__ import annotations
from kivy.uix.button import Button  # type: ignore
from kivy.properties import BooleanProperty

# from kivy.animation import Animation
# from kivy.properties import Clock
# from kivy.graphics import Ellipse, Color

from monster_classes import Monster
from fading_tokens import EffectToken


class Tile(Button):

    dodging_finished = BooleanProperty(False)

    def __init__(self, row, col, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.row: int = row
        self.col: int = col
        self.position: tuple = (row, col)
        self.kind: str = kind
        self.tokens: list = list()
        self.dungeon = dungeon_instance  # need to pass the instance of the dungeon to call dungeon.move_token from the class

    @staticmethod
    def update_token(tile, tile_pos):

        tile.token.pos = tile_pos
        tile.token.size = tile.size

    @property
    def is_activable(self):

        player = self.dungeon.game.active_character

        if self.has_token(("player", None)):

            if player.using_dynamite:
                return False
            if self.get_character() == player:
                return True
            if (
                    self.get_character().has_moved
                    and not Monster.all_dead()
            ):
                return False
            return True

        path = self.dungeon.find_shortest_path(
            self.dungeon.get_tile(player.position).position, self.position, player.blocked_by
        )

        dynamite_path = self.dungeon.find_shortest_path(
            self.dungeon.get_tile(player.position).position,
            self.position,
            tuple(item for item in player.blocked_by if item != "monster"),
        )

        if (
                self.has_token(("wall", "rock"))
                and self.dungeon.are_nearby(self.position, player.position)
                and player.stats.remaining_moves >= player.stats.digging_moves
                and not player.using_dynamite
        ):

            if player.stats.shovels > 0 or "digging" in player.free_actions:
                return True

        if self.has_token(("wall", "granite")) and player.name == "Hawkins":
            if (
                    self.dungeon.are_nearby(self.position, player.position)
                    and player.stats.remaining_moves >= player.stats.digging_moves
                    and player.stats.shovels > 0
            ):
                return True

        if (
                self.has_token(("wall", "granite")) or self.has_token(("wall", "quartz"))
        ) and player.using_dynamite():
            return True

        if (
                self.has_token(("monster", None))
                and self.dungeon.are_nearby(self.position, player.position)
                and (player.stats.weapons > 0 or "fighting" in player.free_actions)
        ):
            return True

        if (
                player.using_dynamite
                and dynamite_path is not None
                and len(dynamite_path) <= player.stats.shooting_range
        ):
            return True

        if path is not None and len(path) <= player.stats.remaining_moves:
            return True

        return False

    def on_release(self):

        player = self.dungeon.game.active_character
        game = self.dungeon.game

        if player.using_dynamite:
            player.special_items["dynamite"] -= 1
            player.stats.remaining_moves -= 1
            player.ability_active = (
                False if player.special_items["dynamite"] == 0 else True
            )
            game.update_switch("ability_button")

            self.fall_dynamite_on_tile()

        elif self.has_token(("player", None)) and self.get_character() != player:
            game.switch_character(self.get_character())

        elif self.has_token(("wall", None)):
            player.dig(self)
            game.update_switch("character_done")

        elif self.has_token(("monster", None)):
            player.fight_on_tile(self)
            game.update_switch("character_done")

        else:
            start_tile = self.dungeon.get_tile(player.position)

            if (
                start_tile.token.kind == "player"
                and start_tile.token.character == player
            ):
                start_tile.token.move_player_token(start_tile, self)

            else:
                start_tile.second_token.move_player_token(start_tile, self)

    def fall_dynamite_on_tile(self):

        if self.has_token(("monster", None)):
            self.get_character().try_to_dodge()
        else:
            self.dodging_finished = True

    def on_dodging_finished(self, *args):

        if self.dodging_finished:
            if self.has_token(("monster", None)):
                self.get_character().kill_character(self)
            self.clear_token()  # remove all other tokens, pickables, etc. if any
            self.dungeon.place_item(self, "wall", "rock", None)
            #self.dungeon.instantiate_character(self, "wall", "rock")
            self.show_explosion()
            self.on_dodging_finished = False

            self.dungeon.game.update_switch("character_done")


    def has_token(self, token: tuple[str,str] | tuple[str,None] | None = None) -> bool:

        if token is None:
            return len(self.tokens) > 0
        kind, species = token
        return any(token.kind == kind and (species is None or token.species == species) for token in self.tokens)

    def clear_token(self, token_kind: str | None = None) -> None:

        if token_kind is None:
            if self.second_token is not None:
                self._delete_token(self.second_token)

            if self.token is not None:
                self._delete_token(self.token)

        elif self.second_token and self.second_token.kind == token_kind:
            self._delete_token(self.second_token)

        elif self.token and self.token.kind == token_kind:
            self._delete_token(self.token)


    def _delete_token(self, token):
        self.dungeon.canvas.remove(token.shape)
        token.remove_selection_circle()
        token.remove_health_bar()
        self.tokens.remove(token)

    def get_character(self) -> Character:
        return next((token.character for token in self.tokens if token.character is not None),None)

    def get_token(self, token_kind: str) -> Token | None:
        """
        This function is intended to return a list of all tokens on the Tile sharing the same token_kind
        In this version of the game two Tokens of the same kind cannot share Tile
        Next versions of the game might consider implementing multiple tokens of same kind on same Tile
        :param token_kind:
        :return:
        """
        tokens = [token for token in self.tokens if token_kind == token_kind]
        return tokens [0]

    def show_explosion(self):
        """
        Shows an explosion
        """
        pass
        #with self.dungeon.canvas:
            #EffectToken("explosion", self.pos, self.size)
