from kivy.uix.button import Button  # type: ignore
from kivy.properties import BooleanProperty

# from kivy.animation import Animation
# from kivy.properties import Clock
# from kivy.graphics import Ellipse, Color

from crapgeon_utils import are_nearby
from monster_classes import Monster


class Tile(Button):

    dodging_finished = BooleanProperty(False)

    def __init__(self, row, col, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.row: int = row
        self.col: int = col
        self.position: tuple = (row, col)
        self.kind: str = kind
        self.token = (
            None  # defined when is by DungeonLayout.create_item
        )
        self.second_token = (
            None  # tiles can have up to 2 tokens (shovel + monster for instance).
        )
        self.dungeon = dungeon_instance  # need to pass the instance of the dungeon to call dungeon.move_token from the class

    def on_release(self):

        player = self.dungeon.game.active_character
        game = self.dungeon.game

        if player.using_dynamite():
            player.special_items["dynamite"] -= 1
            player.stats.remaining_moves -= 1
            player.ability_active = (
                False if player.special_items["dynamite"] == 0 else True
            )
            game.update_switch("ability_button")

            self.fall_dynamite_on_tile()

        elif self.has_token(("player", None)) and self.get_character() != player:
            print("SWITCH CHARACTER")
            print(self.get_character())
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
                start_tile.token.move_player(start_tile, self)

            else:
                start_tile.second_token.move_player(start_tile, self)

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
            self.dungeon.create_item(self, "wall", "rock")
            self.dungeon.show_effect_token(
                "explosion", self.token.shape.pos, self.token.shape.size
            )
            self.on_dodging_finished = False

            self.dungeon.game.update_switch("character_done")

    def update_token(self, tile, tile_pos):

        tile.token.pos = tile_pos
        tile.token.size = tile.size

    def is_activable(self):

        player = self.dungeon.game.active_character

        if self.has_token(("player", None)):

            if player.using_dynamite():
                return False
            if self.get_character() == player:
                return True
            if (
                self.get_character().has_moved()
                and not Monster.all_dead()
            ):
                return False
            return True

        path = self.dungeon.find_shortest_path(
            self.dungeon.get_tile(player.position), self, player.blocked_by
        )

        dynamite_path = self.dungeon.find_shortest_path(
            self.dungeon.get_tile(player.position),
            self,
            tuple(item for item in player.blocked_by if item != "monster"),
        )

        if (
            self.has_token(("wall", "rock"))
            and are_nearby(self, player)
            and player.stats.remaining_moves >= player.stats.digging_moves
            and not player.using_dynamite()
        ):

            if player.stats.shovels > 0 or "digging" in player.free_actions:
                return True

        if self.has_token(("wall", "granite")) and player.name == "Hawkins":
            if (
                are_nearby(self, player)
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
            and are_nearby(self, player)
            and ((player.stats.weapons > 0 or "fighting" in player.free_actions))
        ):
            return True

        if (
            player.using_dynamite()
            and dynamite_path is not None
            and len(dynamite_path) <= player.stats.shooting_range
        ):
            return True

        if path is not None and len(path) <= player.stats.remaining_moves:
            return True

        return False

    def has_token(self, token: tuple[str] | None = None) -> bool:

        if token is None and self.token is not None and self.second_token is not None:
            return True

        if token is not None:

            if self.second_token and self.second_token.kind == token[0]:
                if token[1] is None or self.second_token.species == token[1]:
                    return True
                # else:
                # return False

            if self.token and self.token.kind == token[0]:
                if token[1] is None or self.token.species == token[1]:
                    return True
                # else:
                # return False

        return False

    def clear_token(self, token_kind: str | None = None) -> None:

        if token_kind is None:
            if self.second_token is not None:
                self.dungeon.canvas.remove(self.second_token.shape)
                self.second_token.remove_selection_circle()
                self.second_token.remove_health_bar()
                self.second_token = None
            if self.token is not None:
                self.dungeon.canvas.remove(self.token.shape)
                self.token.remove_selection_circle()
                self.token.remove_health_bar()
                self.token = None

        elif self.second_token and self.second_token.kind == token_kind:
            self.dungeon.canvas.remove(self.second_token.shape)
            self.second_token.remove_selection_circle()
            self.second_token.remove_health_bar()
            self.second_token = None

        elif self.token and self.token.kind == token_kind:
            self.dungeon.canvas.remove(self.token.shape)
            self.token.remove_selection_circle()
            self.token.remove_health_bar()
            self.token = None

    def get_character(self):

        if self.second_token and hasattr(self.second_token, "character"):
            return self.second_token.character
        elif self.token and hasattr(self.token, "character"):
            return self.token.character
