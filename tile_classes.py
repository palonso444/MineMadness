from __future__ import annotations
from kivy.uix.button import Button  # type: ignore
from kivy.properties import BooleanProperty

# from kivy.animation import Animation
# from kivy.properties import Clock
# from kivy.graphics import Ellipse, Color

from monster_classes import Monster
from tokens_fading import EffectToken
from tokens_solid import CharacterToken, SceneryToken


class Tile(Button):

    dodging_finished = BooleanProperty(False)

    def __init__(self, row, col, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.row: int = row
        self.col: int = col
        self.position: tuple = row, col
        self.kind: str = kind
        self.tokens: dict [str:Token | None] = {
            "player": None,
            "monster": None,
            "wall": None,
            "pickable": None,
            "treasure": None
        }
        self.dungeon = dungeon_instance  # need to pass the instance of the dungeon to call dungeon.move_token from the class

    @staticmethod
    def update_tokens_size_and_pos(tile, tile_pos):
        for token in tile.tokens.values():
            if token is not None:
                token.pos = tile_pos
                token.size = tile.size

    def set_token(self, token: Token) -> None:
        self.tokens[token.kind] = token

    def get_token(self, token_kind) -> Token:
        return self.tokens[token_kind]

    def remove_token(self, token_kind) -> None:
        self.tokens[token_kind] = None

    def is_nearby(self, position: tuple[int,int]) -> bool:
        """
        Checks if the given position is nearby to the tile
        :param position: position to check
        :return: True if is nearby, False otherwise
        """
        directions = (-1, 0), (1, 0), (0, -1), (0, 1)

        return any(
            (self.position[0] + dx, self.position[1] + dy) == position
            for dx, dy in directions
        )

    def check_if_enable(self, active_player: Player):

        if self.has_token("player"):
            return self._check_with_player_token(active_player)
        if self.has_token("monster"):
            return self._check_with_monster_token(active_player)
        if self.has_token("wall"):
            return self._check_with_wall_token(active_player)

        return True

    def _check_with_monster_token(self, active_player: Player):

        if active_player.using_dynamite:
            return self.dungeon.check_if_connexion(active_player.token.position,
                                                   self.position,
                                                   active_player.blocked_by,
                                                   active_player.stats.shooting_range)
            # tuple(item for item in player.blocked_by if item != "monster")

        elif self.is_nearby(active_player.token.position):
            return active_player.can_fight(self.get_token("monster").species)

        return False

    def _check_with_wall_token(self, active_player: Player):

        if active_player.using_dynamite:
            return (self.dungeon.check_if_connexion(active_player.token.position,
                                            self.position,
                                            active_player.blocked_by,
                                            active_player.stats.shooting_range) and
            not self.has_token("wall","rock"))

        elif self.is_nearby(active_player.token.position):
            return active_player.can_dig(self.get_token("wall").species)

        return False

    def _check_with_player_token(self, active_player: Player):

        if active_player.using_dynamite:
            return False
        if self.get_token("player").character == active_player:
            return True
        if self.get_token("player").character.has_moved and not Monster.all_dead():
            return False

        return True

    def on_release(self):

        player = self.dungeon.game.active_character
        game = self.dungeon.game

        if player.using_dynamite:
            player.throw_dynamite()
            game.update_switch("ability_button")
            self.fall_dynamite_on_tile()

        elif self.has_token("player") and self.get_token("player").character != player:
            game.switch_character(self.get_token("player"))

        elif self.has_token("wall"):
            player.dig(self)
            game.update_switch("character_done")

        elif self.has_token("monster"):
            player.fight_on_tile(self)
            game.update_switch("character_done")

        else:
            start_tile = self.dungeon.get_tile(player.token.position)

            if start_tile.tokens["player"].character == player:
                start_tile.tokens["player"].move_token(player.token.position, self.position)

    def fall_dynamite_on_tile(self):

        if self.has_token("monster"):
            self.get_token("monster").character.try_to_dodge()
        else:
            self.dodging_finished = True

    def on_dodging_finished(self, *args):

        if self.dodging_finished:
            if self.has_token("monster"):
                self.get_token("monster").character.kill_character(self)
            self.delete_token()  # remove all other tokens, pickables, etc. if any
            self.dungeon.place_item(self, "wall", "rock", None)
            self.show_explosion()
            self.dodging_finished = False

            self.dungeon.game.update_switch("character_done")


    def has_token(self, token_kind: str | None = None, token_species: str | None = None) -> bool:

        if token_kind is None:
            if token_species is not None:
                raise ValueError("token_kind cannot be None and token_species not None")
            return any(token is not None for token in self.tokens.values())

        return (self.tokens[token_kind] is not None and
                (token_species is None or self.tokens[token_kind].species == token_species))



    def show_explosion(self):
        """
        Shows an explosion
        """
        pass
        #with self.dungeon.canvas:
            #EffectToken("explosion", self.pos, self.size)
