from __future__ import annotations
from kivy.uix.button import Button  # type: ignore
from kivy.properties import BooleanProperty

# from kivy.animation import Animation
# from kivy.properties import Clock
# from kivy.graphics import Ellipse, Color

from monster_classes import Monster
from fading_tokens import EffectToken
from solid_tokens import CharacterToken, SceneryToken


class Tile(Button):

    dodging_finished = BooleanProperty(False)

    def __init__(self, row, col, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.row: int = row
        self.col: int = col
        self.position: tuple = (row, col)
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
    def update_tokens(tile, tile_pos):
        for token in tile.tokens.values():
            if token is not None:
                token.pos = tile_pos
                token.size = tile.size

    @property
    def is_activable(self):

        player = self.dungeon.game.active_character

        if self.has_token("player"):

            if player.using_dynamite:
                return False
            if self.tokens["player"].character == player:
                return True
            if (
                    self.tokens["player"].character.has_moved
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
                self.has_token("wall", "rock")
                and self.dungeon.are_nearby(self.position, player.position)
                and player.stats.remaining_moves >= player.stats.digging_moves
                and not player.using_dynamite
        ):

            if player.stats.shovels > 0 or "digging" in player.free_actions:
                return True

        if self.has_token("wall", "granite") and player.name == "Hawkins":
            if (
                    self.dungeon.are_nearby(self.position, player.position)
                    and player.stats.remaining_moves >= player.stats.digging_moves
                    and player.stats.shovels > 0
            ):
                return True

        if (
                self.has_token("wall", "granite") or self.has_token("wall", "quartz")
        ) and player.using_dynamite():
            return True

        if (
                self.has_token("monster")
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

        elif self.has_token("player") and self.tokens["player"].character != player:
            game.switch_character(self.tokens["player"].character)

        elif self.has_token("wall"):
            player.dig(self)
            game.update_switch("character_done")

        elif self.has_token("monster"):
            player.fight_on_tile(self)
            game.update_switch("character_done")

        else:
            start_tile = self.dungeon.get_tile(player.position)

            if start_tile.tokens["player"].character == player:
                start_tile.tokens["player"].move_player_token(start_tile, self)

            #else:
                #start_tile.second_token.move_player_token(start_tile, self)

    def fall_dynamite_on_tile(self):

        if self.has_token("monster"):
            self.tokens["monster"].character.try_to_dodge()
        else:
            self.dodging_finished = True

    def on_dodging_finished(self, *args):

        if self.dodging_finished:
            if self.has_token("monster"):
                self.tokens["monster"].character.kill_character(self)
            self.delete_token()  # remove all other tokens, pickables, etc. if any
            self.dungeon.place_item(self, "wall", "rock", None)
            #self.dungeon.instantiate_character(self, "wall", "rock")
            self.show_explosion()
            self.on_dodging_finished = False

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
