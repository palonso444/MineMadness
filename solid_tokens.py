from __future__ import annotations
from kivy.graphics import Ellipse, Rectangle, Color, Line, VertexInstruction  # type: ignore
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty

from fading_tokens import DamageToken, DiggingToken, EffectToken


class SolidToken(Widget):
    """
    Base class defining all Tokens that stay on the board for extended periods of time
    """
    def __init__(self, kind: str, species:str, character: Character, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(**kwargs)

        self.kind: str = kind
        self.species: str = species
        self.character: Character = character
        self.dungeon: DungeonLayout = dungeon_instance
        self.source: str = "./tokens/" + self.species + "token.png"
        self.shape: VertexInstruction | None = None  # token.shape (canvas object) initialized in each subclass

    @staticmethod
    def update_pos(solid_token, solid_token_pos) -> None:
        """
        Callback updating the position of the shape of the Token upon positioning on the board
        :param solid_token: SolidToken to update size and position of its shape
        :param solid_token_pos: position of the token
        :return: None
        """
        solid_token.shape.pos = solid_token_pos

    def get_current_tile(self) -> Tile:
        """
        Returns the Tile corresponding to the current position of the Token
        :return:
        """
        return self.dungeon.get_tile(self.character.position)

    def delete_token(self, tile: Tile) -> None:
        """
        Completely erases the Token from the game
        :param tile: Tile in which the Token is located
        :return: None
        """
        tile.tokens[self.kind] = None
        self.dungeon.canvas.remove(self.shape)

class SceneryToken(SolidToken):
    """
    Base class defining Tokens without associated Character
    """
    def __init__(self, kind: str, species: str, character: None, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, character, dungeon_instance, **kwargs)

        with self.dungeon.canvas:
            self.shape = Rectangle(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update_pos)

    def show_digging(self) -> None:
        """
        Shows the on the Token the FadingToken corresponding to the digging action of a Player
        :return: None
        """
        with self.dungeon.canvas.after:
            DiggingToken(pos=self.pos, size=self.size, dungeon=self)


class CharacterToken(SolidToken):
    """
    Base class defining all Tokens with associated Character
    """
    def __init__(self, kind: str, species: str, character: CharacterToken,
                 dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, character, dungeon_instance, **kwargs)

        self.start: Tile | None = None  # all defined when token is moved by move()
        self.goal: Tile | None = None
        self.path: list[tuple[int,int]] | None = None

        with self.dungeon.canvas:
            self.color = Color(1, 1, 1, 1)
            self.shape = Ellipse(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update_pos)


    def slide(self) -> Animation:
        """
        Instantiates the Animation object to slide the Token 1 step along the route determined in CharacterToken.path
        :return: Animation object ready to start
        """
        self.character.stats.remaining_moves -= 1
        next_tile: Tile = self.dungeon.get_tile(self.path.pop(0))
        animation = Animation(pos=next_tile.pos, duration=0.2)
        animation.bind(on_complete=self.on_slide_completed)
        return animation

    def on_slide_completed(self, animation: Animation, token_shape:VertexInstruction) -> None:
        """
        Callback triggered when the slide is completed on Character turn
        :return: None
        """
        if len(self.path) > 0:
            self.slide()
        else:
            if self.start != self.goal: # update position if goal is reached
                self.start.tokens[self.kind]: Token | None = None
                self.goal.tokens[self.kind]: Token | None = self
                self.character.position = self.goal.position
                self.pos: tuple[int,int] = self.shape.pos

                self.start: Tile | None = None
                self.goal: Tile | None = None
                self.path: list[tuple[int,int]] | None = None

                self.character.behave(self.get_current_tile())

            self.dungeon.game.update_switch("character_done")

    def show_damage(self) -> None:
        """
        Shows the on the Token the FadingToken corresponding to damage
        :return: None
        """
        with self.dungeon.canvas.after:
            DamageToken(pos=self.pos, size=self.size, dungeon=self)


class PlayerToken(CharacterToken):
    """
    Class defining Tokens representing Players
    """
    percentage_natural_health = NumericProperty(None)
    fading_tokens_queue = ListProperty([])

    def __init__(self, kind: str, species: str, character: Character,
                 dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, character, dungeon_instance, **kwargs)

        self.circle: VertexInstruction | None = None
        self.circle_color: VertexInstruction | None = None
        self.green_bar: VertexInstruction | None = None
        self.red_bar: VertexInstruction | None = None

        self.bind(percentage_natural_health=self.display_health_bar)
        self.post_init()

    def post_init(self):
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

    @staticmethod
    def display_health_bar(player_token, percentage_natural_health):

        if player_token.green_bar is not None and player_token.red_bar is not None:
            player_token.remove_health_bar()

        bar_pos_x = player_token.pos[0] + (player_token.size[0] * 0.1)
        bar_pos_y = player_token.pos[1] + (player_token.size[1] * 0.1)

        bar_length = player_token.size[0] * 0.8  # total horizontal length of the bar
        bar_thickness = player_token.size[1] * 0.1

        # canvas.after to ensure bar is displayed on top of charactertoken
        with player_token.dungeon.canvas.after:

            # green portion of health bar
            player_token.bar_color = Color(0, 1, 0, 1)
            player_token.green_bar = Rectangle(
                pos=(bar_pos_x, bar_pos_y),
                size=(bar_length * percentage_natural_health, bar_thickness),
            )

            # red portion of health bar
            player_token.bar_color = Color(1, 0, 0, 1)
            player_token.red_bar = Rectangle(
                # x position of red bar is bar_pos_x + length of green portion of bar
                pos=(bar_pos_x + player_token.green_bar.size[0], bar_pos_y),
                size=(bar_length * (1 - percentage_natural_health), bar_thickness),
            )

        player_token.bind(pos=player_token.update_health_bar, size=player_token.update_health_bar)

    def update_health_bar(self, *args):

        # update green portion of health bar
        self.green_bar.pos = (
            self.shape.pos[0] + self.size[0] * 0.1,
            self.shape.pos[1] + self.size[1] * 0.1,
        )
        self.green_bar.size = (
            self.size[0] * 0.8 * self.percentage_natural_health,
            self.size[1] * 0.1,
        )

        # update red portion of health bar
        self.red_bar.pos = (
            # x position of bar is token_pos + 0.1 margin + size of green portion of bar
            self.shape.pos[0] + (self.size[0] * 0.1) + self.green_bar.size[0],
            self.shape.pos[1] + (self.size[1] * 0.1),
        )
        self.red_bar.size = (
            self.size[0] * 0.8 * (1 - self.percentage_natural_health),
            self.size[1] * 0.1,
        )

    def remove_health_bar(self):

        for bar in [self.green_bar, self.red_bar]:
            self.dungeon.canvas.after.remove(bar)
        self.green_bar = None
        self.red_bar = None

    def draw_selection_circle(self):

        with self.dungeon.canvas:
            self.circle_color = Color(1, 1, 0, 1)
            self.circle = Line(
                circle=(
                    self.pos[0] + self.width / 2,
                    self.pos[1] + self.height / 2,
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
        self.dungeon.canvas.remove(self.circle)
        self.circle = None
        self.circle_color = None

    def delete_token(self, tile: Tile):
        super().delete_token(tile)
        if self.circle is not None:  # to avoid interferences with MineMadnessGame.on_character_done()
            self.remove_selection_circle()
        self.remove_health_bar()

    def move_player_token(self, start_tile, end_tile):

        if start_tile == end_tile:  # if character stays in place
            self.character.stats.remaining_moves = 0
            self.dungeon.game.update_switch("character_done")

        else:
            self.start = start_tile
            self.goal = end_tile
            start_tile.tokens[self.kind] = None
            self.path = self.dungeon.find_shortest_path(
                start_tile.position, end_tile.position, self.character.blocked_by
            )
            self.dungeon.activate_which_tiles()  # tiles disabled while moving

            self.slide()


    def slide(self):
        animation = super().slide()
        animation.bind(on_progress=self.update_circle)
        animation.bind(on_progress=self.update_health_bar)
        animation.start(self.shape)


class MonsterToken(CharacterToken):
    """
    Class defining Tokens representing Monsters
    """
    def __init__(self, kind, species, character, dungeon_instance, **kwargs):
        super().__init__(kind, species, character, dungeon_instance, **kwargs)

    def move_monster_token(self):

        self.start = self.dungeon.get_tile(self.character.position)
        self.path = self.character.move()

        if self.path is None:  # if it cannot move, will try directly to attack players
            self.character.behave(self.start)

        else:
            goal_index = (
                self.character.stats.remaining_moves - 1
                if self.character.stats.remaining_moves - 1 < len(self.path)
                else len(self.path) - 1
            )
            self.goal = self.dungeon.get_tile(self.path[goal_index])

            self.slide()

    def slide(self):
        animation = super().slide()
        animation.start(self.shape)
