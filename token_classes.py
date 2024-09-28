from kivy.graphics import Ellipse, Rectangle, Color, Line  # type: ignore
from kivy.animation import Animation

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty

from crapgeon_utils import check_if_multiple


class SolidToken(Widget):

    def __init__(self, kind, species, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind  # defines if pickable or wall
        self.species = species
        self.dungeon = dungeon_instance
        self.source = "./tokens/" + self.species + "token.png"

        self.shape = None  # token.shape (canvas object) initialized in each subclass
        self.circle = None  # token.circle (canvas object) initialized by draw_selection_circle() only in players
        # SceneryToken need this attribute to avoid bugs in Player.dig() and Player.pick_object()

    def update(self, solidtoken, solidtoken_pos):
        solidtoken.shape.pos = solidtoken_pos
        solidtoken.shape.size = solidtoken.size

    def remove_selection_circle(self):
        """
        Placeholder to avoid crashing by Tile.clear_token()
        """
        pass

    def remove_health_bar(self):
        """
        Placeholder to avoid crashing by Tile.clear_token()
        """
        pass


class FadingToken(Widget):

    def __init__(self, dungeon, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.final_opacity = None
        self.dungeon = dungeon
        self.duration: int | None = None

    def fade(self):

        def fade_out(*args):

            fading = Animation(opacity=0, duration=self.duration)
            if isinstance(self, EffectToken):
                # remove item from Dungeon.fading_tokens_items_queue
                fading.bind(on_complete=self.dungeon.remove_item_if_in_queue)
            fading.start(self)

        fading = Animation(opacity=self.final_opacity, duration=self.duration)
        fading.bind(on_complete=fade_out)
        fading.start(self)


class DamageToken(FadingToken):

    def __init__(self, dungeon, **kwargs):
        super().__init__(dungeon, **kwargs)
        self.final_opacity = 0.4
        self.duration = 0.2

        with self.canvas:
            self.color = Color(1, 0, 0, 1)
            self.shape = Ellipse(pos=self.pos, size=self.size)

        self.fade()


class DiggingToken(FadingToken):

    def __init__(self, dungeon, **kwargs):
        super().__init__(dungeon, **kwargs)
        self.final_opacity = 0.7
        self.duration = 0.2

        with self.canvas:
            self.color = Color(0.58, 0.294, 0, 1)
            self.shape = Rectangle(pos=self.pos, size=self.size)

        self.fade()


class EffectToken(FadingToken):
    """
    Introduce as item argument the name of the item that causes the effect (example: coffee)
    In case of items with more than 1 possible effects, introduce as "item" name_effect (example: talisman_level_up)
    """

    def __init__(self, item: str, dungeon, effect_fades: bool = False, **kwargs):
        super().__init__(dungeon, **kwargs)
        self.final_opacity = 1
        self.duration = 0.6
        self.item = item

        if effect_fades:
            self.source = "./fadingtokens/" + self.item + "_fades_token.png"
        else:
            self.source = "./fadingtokens/" + self.item + "_effect_token.png"

        with self.canvas:
            self.shape = Rectangle(pos=self.pos, size=self.size, source=self.source)

        self.fade()


class SceneryToken(SolidToken):

    def __init__(self, kind, species, dungeon_instance, **kwargs):
        super().__init__(kind, species, dungeon_instance, **kwargs)

        with self.dungeon.canvas:
            self.shape = Rectangle(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update, size=self.update)


class CharacterToken(SolidToken):

    percentage_natural_health = NumericProperty(None)

    def __init__(self, kind, species, character, dungeon_instance, **kwargs):
        from player_classes import Player # TODO: remove this local import
        super().__init__(kind, species, dungeon_instance, **kwargs)

        self.character = character  # links token with character object

        self.start = None  # all defined when token is moved by move()
        self.goal = None
        self.path = None

        self.bar = None  # health bar, monsters need it None to avoid crashing when Token.slide()
        self.negative_bar = None  # red portion of the health bar

        with self.dungeon.canvas:
            self.color = Color(1, 1, 1, 1)
            self.shape = Ellipse(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update, size=self.update)

        if isinstance(self.character, Player):
            # bind and initialize health bar
            self.bind(percentage_natural_health=self.calculate_and_display_health_bar)
            self.percentage_natural_health = (
                self.character.stats.health / self.character.stats.natural_health
            )

    def calculate_and_display_health_bar(self, instance, percentage_natural_health):

        if self.bar is not None and self.negative_bar is not None:
            self.remove_health_bar()

        bar_pos_x = self.shape.pos[0] + (self.shape.size[0] * 0.1)
        bar_pos_y = self.shape.pos[1] + (self.shape.size[1] * 0.1)

        bar_length = self.shape.size[0] * 0.8  # total horizontal length of the bar
        bar_tickness = self.shape.size[1] * 0.1

        # canvas.after to ensure bar is displayed on top of charactertoken
        with self.dungeon.canvas.after:

            # green portion of health bar
            self.bar_color = Color(0, 1, 0, 1)
            self.bar = Rectangle(
                pos=(bar_pos_x, bar_pos_y),
                size=(bar_length * percentage_natural_health, bar_tickness),
            )

            # red portion of health bar
            self.bar_color = Color(1, 0, 0, 1)
            self.negative_bar = Rectangle(
                # x positon of red bar is bar_pos_x + length of green portion of bar
                pos=(bar_pos_x + self.bar.size[0], bar_pos_y),
                size=(bar_length * (1 - percentage_natural_health), bar_tickness),
            )

        self.bind(pos=self.update_health_bar, size=self.update_health_bar)

    def update_health_bar(self, *args):

        # update green portion of health bar
        self.bar.pos = (
            self.shape.pos[0] + self.shape.size[0] * 0.1,
            self.shape.pos[1] + self.shape.size[1] * 0.1,
        )
        self.bar.size = (
            self.shape.size[0] * 0.8 * self.percentage_natural_health,
            self.shape.size[1] * 0.1,
        )

        # update red portion of health bar
        self.negative_bar.pos = (
            # x positon of bar is token_pos + 0.1 margin + size of green portion of bar
            self.shape.pos[0] + (self.shape.size[0] * 0.1) + self.bar.size[0],
            self.shape.pos[1] + (self.shape.size[1] * 0.1),
        )
        self.negative_bar.size = (
            self.shape.size[0] * 0.8 * (1 - self.percentage_natural_health),
            self.shape.size[1] * 0.1,
        )

    def draw_selection_circle(self):

        with self.dungeon.canvas:
            self.circle_color = Color(1, 1, 0, 1)
            self.circle = Line(
                circle=(
                    self.shape.pos[0] + self.width / 2,
                    self.shape.pos[1] + self.height / 2,
                    self.width / 2,
                ),
                width=1.5,
            )

        self.bind(pos=self.update_circle, size=self.update_circle)

    def update_circle(self, *args):

        self.circle.circle = (  # self is CharacterToken, self.circle is Line
            self.shape.pos[0]  # center_x of circle = CharacterToken.pos[0] (x)
            + self.width / 2,
            self.shape.pos[1]  # center_y of circle = CharacterToken.pos[1] (y)
            + self.height / 2,
            self.width / 2,  # radius of circle = CharacterToken.width / 2
        )

    def remove_selection_circle(self):

        if self.circle is not None:
            self.dungeon.canvas.remove(self.circle)
            self.circle = None

    def remove_health_bar(self):

        if self.bar is not None:
            self.dungeon.canvas.after.remove(self.bar)
            self.bar = None

        if self.negative_bar is not None:
            self.dungeon.canvas.after.remove(self.negative_bar)
            self.negative_bar = None

    def move_player(self, start_tile, end_tile):

        if start_tile == end_tile:  # if character stays in place

            self.character.stats.remaining_moves = 0
            self.dungeon.game.update_switch("character_done")

        else:

            self.start = start_tile
            self.goal = end_tile

            self.path = self.dungeon.find_shortest_path(
                self.start, self.goal, (self.character.blocked_by)
            )

            self.dungeon.activate_which_tiles()  # tiles desactivated while moving

            self.slide(self.path)

    def move_monster(self):

        self.start = self.dungeon.get_tile(self.character.position)
        self.path = self.character.move()

        if self.path is None:  # if cannot move, will try directly to attack players
            self.character.attack_players()
            self.dungeon.game.update_switch("character_done")

        else:

            goal_index = (
                self.character.stats.remaining_moves - 1
                if self.character.stats.remaining_moves - 1 < len(self.path)
                else len(self.path) - 1
            )
            self.goal = self.dungeon.get_tile(self.path[goal_index])

            self.slide(self.path)

    def slide(self, path):

        next_tile = self.dungeon.get_tile(path.pop(0))
        next_pos = next_tile.pos

        if self.character.stats.remaining_moves is not None:  # sometimes when dodging
            self.character.stats.remaining_moves -= 1

        animation = Animation(pos=next_pos, duration=0.2)
        if self.circle is not None:  # selection circle
            animation.bind(on_progress=self.update_circle)
        if self.bar is not None:  # health bar
            animation.bind(on_progress=self.update_health_bar)
        animation.bind(on_complete=self.on_slide_completed)
        animation.start(self.shape)

    def on_slide_completed(self, *args):
        from player_classes import Player #TODO: remove those local imports, move this function to main.py
        from monster_classes import Monster
        game = self.dungeon.game
        monster_dodged = False

        # len(path) is always <= monster.stats.remaining_moves
        if len(self.path) > 0:
            self.slide(self.path)

        else:  # if goal is reached

            if isinstance(self.character, Player):

                if (
                    self.goal.kind == "exit"
                    and Player.gems == game.total_gems
                ):

                    self.update_on_tiles(self.start, self.goal)  # updates tile.token
                    self.character.update_position(self.goal.position)
                    game.update_switch("player_exited")
                    return

                elif self.goal.has_token(("pickable", None)):
                    self.character.pick_object(self.goal)

            if self.start != self.goal:
                self.update_on_tiles(self.start, self.goal)  # updates tile.token
                self.character.update_position(self.goal.position)

            # only attack in monster turn, no attack if dodging
            if isinstance(self.character, Monster):

                # if players turn, monster was dodging
                if check_if_multiple(game.turn, 2):
                    self.dungeon.get_tile(self.start.position).dodging_finished = True
                    monster_dodged = True
                else:
                    self.character.attack_players()

            # if monster dodged switch is updated in "on_dodging_finished()"
            if not monster_dodged:
                game.update_switch("character_done")

    def update_on_tiles(self, start_tile, end_tile):

        if end_tile.token and (
            end_tile.token.kind in self.character.ignores
            or end_tile.token.species in self.character.ignores
        ):
            end_tile.second_token = self
        else:
            end_tile.token = self

        if start_tile.second_token:
            start_tile.second_token = None
        else:
            start_tile.token = None
