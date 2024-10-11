from __future__ import annotations
from kivy.graphics import Ellipse, Rectangle, Color, Line  # type: ignore
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty

from crapgeon_utils import check_if_multiple
from fading_tokens import DamageToken, DiggingToken, EffectToken


class SolidToken(Widget):

    def __init__(self, kind, species, character: Character, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind  # defines if pickable or wall
        self.species = species
        self.character = character
        self.dungeon = dungeon_instance
        self.source = "./tokens/" + self.species + "token.png"

        self.shape = None  # token.shape (canvas object) initialized in each subclass
        self.circle = None  # token.circle (canvas object) initialized by draw_selection_circle() only in players
        # SceneryToken need this attribute to avoid bugs in Player.dig() and Player.pick_object()

    @staticmethod
    def update(solidtoken, solidtoken_pos):
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

class SceneryToken(SolidToken):

    def __init__(self, kind, species, character, dungeon_instance, **kwargs):
        super().__init__(kind, species, character, dungeon_instance, **kwargs)

        with self.dungeon.canvas:
            self.shape = Rectangle(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update, size=self.update)

    def show_digging(self):
        with self.dungeon.canvas:
            DiggingToken(pos=self.pos, size=self.size, dungeon=self)


class CharacterToken(SolidToken):

    def __init__(self, kind, species, character, dungeon_instance, **kwargs):
        super().__init__(kind, species, character, dungeon_instance, **kwargs)

        self.start = None  # all defined when token is moved by move()
        self.goal = None
        self.path = None

        with self.dungeon.canvas:
            self.color = Color(1, 1, 1, 1)
            self.shape = Ellipse(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update, size=self.update)

    def slide(self, path):
        """
        This should be abstractmethod when resolved metaclass conflict
        :return: None
        """
        next_tile = self.dungeon.get_tile(path.pop(0))
        next_pos = next_tile.pos

        if self.character.stats.remaining_moves is not None:  # sometimes when dodging
            self.character.stats.remaining_moves -= 1

        animation = Animation(pos=next_pos, duration=0.2)
        animation.bind(on_complete=self.on_slide_completed)
        return animation

    def on_slide_completed(self, *args):
        """
        This should be abstractmethod when resolved metaclass conflict
        :return: None
        """
        # len(path) is always <= monster.stats.remaining_moves
        if len(self.path) > 0:
            self.slide(self.path)
            return False

        elif self.start != self.goal: # update position if goal is reached
            self.update_on_tiles(self.start, self.goal)  # updates tile.token
            self.character.position = self.goal.position
            self.pos = self.shape.pos  # updates pos of Token according to its shape
            print("TOKEN POS (self.pos)")
            print(self.pos)
            print("SHAPE POS (self.shape.pos)")
            print(self.shape.pos)
            return True

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

    def show_damage(self):
        with self.dungeon.canvas:
            DamageToken(pos=self.pos, size=self.size, dungeon=self)


class PlayerToken(CharacterToken):

    percentage_natural_health = NumericProperty(None)
    fading_tokens_queue = ListProperty([])

    def __init__(self, kind, species, character, dungeon_instance, **kwargs):
        super().__init__(kind, species, character, dungeon_instance, **kwargs)

        self.bar = None  # health bar, monsters need it None to avoid crashing when Token.slide()
        self.negative_bar = None  # red portion of the health bar
        self.bind(percentage_natural_health=self.calculate_and_display_health_bar)
        self.percentage_natural_health = (
                self.character.stats.health / self.character.stats.natural_health
        )


    @staticmethod
    def on_fading_tokens_queue(character_token, fading_tokens_queue):
        if len(fading_tokens_queue) > 0:
            character_token.show_effect_token(fading_tokens_queue[0], character_token.pos,
                                              character_token.size, effect_ends=True)

    def remove_token_if_in_queue(self, animation, fading_token):
        """
        Bound to end of fading_out animation
        :param animation:
        :param fading_token:
        :return:
        """
        if fading_token.item in self.fading_tokens_queue:
            self.fading_tokens_queue.remove(fading_token.item)

    def show_effect_token(self, item, pos, size, effect_ends=False):
        """
        Item is the item causing effect, see tokens.EffectToken class for more details.
        """
        with self.dungeon.canvas:
            EffectToken(item=item, pos=pos, size=size, character_token=self, effect_ends=effect_ends)


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

    def move_player_token(self, start_tile, end_tile):

        if start_tile == end_tile:  # if character stays in place
            self.character.stats.remaining_moves = 0
            self.dungeon.game.update_switch("character_done")

        else:
            self.start = start_tile
            self.goal = end_tile
            self.path = self.dungeon.find_shortest_path(
                self.start.position, self.goal.position, self.character.blocked_by
            )
            self.dungeon.activate_which_tiles()  # tiles desactivated while moving

            self.slide(self.path)


    def slide(self, path):
        animation = super().slide(path)
        animation.bind(on_progress=self.update_circle)
        animation.bind(on_progress=self.update_health_bar)
        animation.start(self.shape)

    def on_slide_completed(self, *args):
        goal_reached = super().on_slide_completed(*args)

        if goal_reached:
            print(self.goal.has_token(("pickable", None)))
            game = self.dungeon.game
            if self.goal.kind == "exit" and self.character.has_all_gems:

                self.update_on_tiles(self.start, self.goal)  # updates tile.token
                self.character.position = self.goal.position
                game.update_switch("player_exited")
                return

            elif self.goal.has_token(("pickable", None)):
                print("PICK OBJECT")
                self.character.pick_object(self.goal)

            self.dungeon.game.update_switch("character_done")


class MonsterToken(CharacterToken):

    def __init__(self, kind, species, character, dungeon_instance, **kwargs):
        super().__init__(kind, species, character, dungeon_instance, **kwargs)

    def move_monster_token(self, start_tile = None, end_tile = None):

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
        animation = super().slide(path)
        animation.start(self.shape)

    def on_slide_completed(self, *args):
        goal_reached = super().on_slide_completed(*args)

        if goal_reached:
            game = self.dungeon.game
            if check_if_multiple(game.turn, 2): # if players turn, monster was dodging
                self.dungeon.get_tile(self.start.position).dodging_finished = True
            else:
                self.character.attack_players()
                self.dungeon.game.update_switch("character_done")

