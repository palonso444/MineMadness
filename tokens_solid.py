from __future__ import annotations
from abc import ABC, ABCMeta, abstractmethod
from audioop import reverse

from kivy.graphics import Ellipse, Rectangle, Color, Line  # type: ignore
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty

from tokens_fading import DamageToken, DiggingToken, EffectToken

class WidgetABCMeta(ABCMeta,type(Widget)):
    """
    Base metaclass allowing to make SolidToken an abstract class (otherwise there is conflict because inherits from
    Widget, so it cannot inherit from ABC inherently)
    """
    pass

class SolidToken(Widget, ABC, metaclass=WidgetABCMeta):
    """
    Base abstract class defining all Tokens that stay on the board for extended periods of time
    """
    def __init__(self, kind: str, species:str, position: tuple[int,int],
                 character: Character, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(**kwargs)

        self.kind: str = kind
        self.species: str = species
        self.position: tuple [int:int] = position
        self.character: Character = character
        self.dungeon: DungeonLayout = dungeon_instance
        self.source: str = "./tokens/" + self.species + "token.png"
        self.shape: Ellipse | Rectangle | None = None  # token.shape (canvas object) initialized in each subclass

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
        return self.dungeon.get_tile(self.position)   # this won't work for SceneryTokens! position attribute for Tokens

    def delete_token(self, tile: Tile) -> None:
        """
        Completely erases the Token from the game
        :param tile: Tile in which the Token is located
        :return: None
        """
        tile.remove_token(self)
        self.dungeon.canvas.remove(self.shape)

class SceneryToken(SolidToken):
    """
    Base class defining Tokens without associated Character
    """
    def __init__(self, kind: str, species: str, position: tuple[int,int],
                 character: None, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, position, character, dungeon_instance, **kwargs)

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


class CharacterToken(SolidToken, ABC, metaclass=WidgetABCMeta):
    """
    Base abstract class defining all Tokens with associated Character. It represents all the aspects related
    to their physical representation on the board (picture, position, health bar(if applicable)) and its movement
    """
    def __init__(self, kind: str, species: str, position: tuple[int,int], character: Character,
                 dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, position, character, dungeon_instance, **kwargs)
        self.path: list[tuple[int,int]] | None = None

        with self.dungeon.canvas:
            self.color = Color(1, 1, 1, 1)
            self.shape = Ellipse(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update_pos)

    @abstractmethod
    def slide_one_step(self) -> None:
        """
        Abstractmethod for starting the slide animation
        :return: None
        """
        pass

    def update_token_on_tile(self, tile : Tile) -> None:
        tile.set_token(self)
        self.position = tile.position
        self.pos: tuple[int, int] = self.shape.pos
        self.path: list[tuple[int, int]] | None = None

    def on_slide_completed(self, animation_obj: Animation,
                           token_shape: Ellipse,
                           current_tile: Tile) -> None:
        """
        Callback triggered when the slide is completed on Character turn. Handles behavior of Character depending
        on Tile.kind
        :return: None
        """
        if len(self.path) > 0 and self.character.stats.remaining_moves > 0:
            self.slide_one_step()

        # on tile release check that avoid moving character if is not meant to move
        else:
            self.update_token_on_tile(current_tile)

            if current_tile.kind == "exit" and self.character.has_all_gems:
                self.character.exit_level()
                self.dungeon.game.update_switch("player_exited")
            else:
                self.character.behave(current_tile)
                self.dungeon.game.update_switch("character_done")

    def show_damage(self) -> None:
        """
        Shows the on the Token the FadingToken corresponding to damage
        :return: None
        """
        with self.dungeon.canvas.after:
            DamageToken(pos=self.pos, size=self.size, dungeon=self)

    def _setup_movement_animation(self) -> Animation:
        """
        Instantiates the Animation object to slide the Token 1 step along the route determined in CharacterToken.path
        :return: Animation object ready to start
        """
        next_tile: Tile = self.dungeon.get_tile(self.path.pop(0))
        animation = Animation(pos=next_tile.pos, duration=0.2)
        animation.bind(on_complete=lambda animation_obj, token_shape: self.on_slide_completed(animation,
                                                                                          token_shape,
                                                                                          next_tile))
        return animation

class PlayerToken(CharacterToken):
    """
    Class defining Tokens representing Players
    """
    remaining_health = NumericProperty(None)
    modified_attributes = ListProperty([])

    def __init__(self, kind: str, species: str, character: Player, position: tuple[int,int],
                 dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, position, character, dungeon_instance, **kwargs)

        self.circle: Line | None = None
        self.circle_color: Line | None = None
        self.green_bar: Rectangle | None = None
        self.red_bar: Rectangle | None = None

        self.bind(remaining_health=self._display_health_bar)
        self.post_init()

    def post_init(self) -> None:
        """
        Changes the value of remaining_health to initialize health bar
        :return: None
        """
        self.remaining_health = (
                self.character.stats.health / self.character.stats.natural_health
        )

    @staticmethod
    def on_modified_attributes(character_token: CharacterToken, modified_attributes: list[str]) -> None:
        """
        Shows FadingTokens for the effect modifying the next attribute on the queue
        :param character_token: CharacterToken on which FadingToken is shown
        :param modified_attributes: queue of currently modified attributes
        :return: 
        """
        if len(modified_attributes) > 0:
            character_token.show_effect_token(modified_attributes[0], character_token.pos,
                                              character_token.size, effect_ends=True)

    def remove_attribute_if_in_queue(self, animation: Animation, fading_token:FadingToken) -> None:
        """
        Triggered when fading_out animation of FadingToken is completed
        :param animation: animation object of fading_out
        :param fading_token: FadingToken fading out
        :return: None
        """
        if fading_token.target_attr in self.modified_attributes:
            self.modified_attributes.remove(fading_token.target_attr)

    def show_effect_token(self, attribute: str, pos: tuple [float,float],
                          size: tuple [float,float], effect_ends: bool =False) -> None:
        """
        Shows the FadingToken of the effect modifying the specified character attribute
        :param attribute: attribute being modified
        :param pos: position of (on the screen) of the CharacterToken that shows the FadingToken
        :param size: size of the CharacterToken that shows the FadingToken
        :param effect_ends: specifies if the effect ends (red FadingToken) of begins (green FadingToken)
        :return: 
        """
        with self.dungeon.canvas:
            EffectToken(target_attr=attribute, pos=pos, size=size, character_token=self, effect_ends=effect_ends)

    @staticmethod
    def _display_health_bar(token: PlayerToken, percent_natural_health: float) -> None:
        """
        Callback triggered when Player.percent_natural_health is modified. Displays the updated health_bar
        depending on the current percent_natural_health
        :param token: PlayerToken showing the bar
        :param percent_natural_health: current percent_natural_health
        :return: None
        """
        if token.green_bar is not None and token.red_bar is not None:
            token._remove_health_bar()

        bar_pos_x = token.pos[0] + (token.size[0] * 0.1)
        bar_pos_y = token.pos[1] + (token.size[1] * 0.1)
        bar_length = token.size[0] * 0.8  # total horizontal length of the bar
        bar_thickness = token.size[1] * 0.1

        with token.dungeon.canvas.after:
            token.bar_color = Color(0, 1, 0, 1)  # green
            token.green_bar = Rectangle(
                pos=(bar_pos_x, bar_pos_y),
                size=(bar_length * percent_natural_health, bar_thickness),
            )
            token.bar_color = Color(1, 0, 0, 1)  # red
            token.red_bar = Rectangle(
                # x position of red bar is bar_pos_x + length of green portion of bar
                pos=(bar_pos_x + token.green_bar.size[0], bar_pos_y),
                size=(bar_length * (1 - percent_natural_health), bar_thickness),
            )

        token.bind(pos=token._move_health_bar, size=token._move_health_bar)

    def _move_health_bar(self, *args) -> None:
        """
        Callback triggered during sliding animation. Moves the health_bar along with the PlayerToken
        :param args: This function receives variable number of arguments. They cannot be typehint
        :return: None
        """
        self.green_bar.pos = (
            self.pos[0] + self.size[0] * 0.1,
            self.pos[1] + self.size[1] * 0.1,
        )
        self.red_bar.pos = (
            # x position of bar is token_pos + 0.1 margin + size of green portion of bar
            self.pos[0] + (self.size[0] * 0.1) + self.green_bar.size[0],
            self.pos[1] + (self.size[1] * 0.1),
        )

    def _remove_health_bar(self) -> None:
        """
        Removes the health bar
        :return: None
        """
        self.dungeon.canvas.after.remove(self.green_bar)
        self.dungeon.canvas.after.remove(self.red_bar)
        self.green_bar = None
        self.red_bar = None

    def display_selection_circle(self) -> None:
        """
        Displays the selection circle around the CharacterToken
        :return: None
        """
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

        self.bind(pos=self._move_selection_circle, size=self._move_selection_circle)

    def _move_selection_circle(self, *args) -> None:
        """
        Callback triggered during sliding animation. Moves the selection_circle along with the PlayerToken
        :param args: This function receives variable number of arguments. They cannot be typehint
        :return: None
        """
        self.circle.circle = (  # self is CharacterToken, self.circle is Line
            self.pos[0]  # center_x of circle = CharacterToken.pos[0] (x)
            + self.width / 2,
            self.pos[1]  # center_y of circle = CharacterToken.pos[1] (y)
            + self.height / 2,
            self.width / 2,  # radius of circle = CharacterToken.width / 2
        )

    def remove_selection_circle(self) -> None:
        """
        Removes the selection circle
        :return: None
        """
        self.dungeon.canvas.remove(self.circle)
        self.circle = None
        self.circle_color = None

    def delete_token(self, tile: Tile) -> None:
        """
        Completely erases the PlayerToken from the board along with the health bar and the selection circle
        :param tile: Tile in which the PlayerToken is located
        :return: None
        """
        super().delete_token(tile)
        if self.circle is not None:  # to avoid interferences with MineMadnessGame.on_character_done()
            self.remove_selection_circle()
        if self.green_bar is not None and self.red_bar is not None:
            self._remove_health_bar()

    def get_movement_range(self, steps: int) -> set[tuple[int,int]]:
        """
        Returns a set with all the potential positions of the Tiles where the Token can move
        :param steps: remaining_moves of the Token.Character
        :return: set with the positions of all Tiles within movement range
        """
        mov_range: set = self._get_horizontal_range(self.position[0], steps)  # row where token is

        vertical_shift: int = 1
        for lateral_steps in range(steps, 0, -1): # 0 is not inclusive but Token row is already added

            y_position: int = self.position [0] - vertical_shift  # move upwards
            if y_position >= 0:
                mov_range = mov_range.union(self._get_horizontal_range(y_position, lateral_steps))

            y_position = self.position[0] + vertical_shift  # move downwards
            if y_position < self.dungeon.rows:
                mov_range = mov_range.union(self._get_horizontal_range(y_position, lateral_steps))

            vertical_shift += 1

        return mov_range

    def _get_horizontal_range(self, y_position: int, lateral_steps: int) -> set[tuple[int,int]]:
        """
        Returns the positions of all Tiles within a row and within the range given by lateral_steps
        :param y_position: y_axis value of the row. x_axis is where the Token sits.
        :param lateral_steps: number of steps to take to each side
        :return: set with all the Tile positions within the row
        """
        horizontal_range: set = set()

        for step in range(0, lateral_steps):
            if self.position[1] - step >= 0:
                horizontal_range.add((y_position, self.position[1] - step)) # add whole row left

            if self.position[1] + step < self.dungeon.cols:
                horizontal_range.add((y_position, self.position[1] + step))  # add whole row right

        return horizontal_range

    def token_move(self, start_position: tuple [int,int], end_position: tuple[int,int]) -> None:
        """
        Initializes the movement of the PlayerToken
        :param start_position: starting position
        :param end_position: target position
        :return: None
        """
        if start_position == end_position:  # if character stays in place
            self.character.stats.remaining_moves = 0
            self.dungeon.game.update_switch("character_done")

        else:
            self.dungeon.get_tile(start_position).remove_token(self)
            self.path = self.dungeon.find_shortest_path(
                start_position, end_position, self.character.blocked_by
            )
            self.dungeon.disable_all_tiles()  # tiles disabled while moving
            self.slide_one_step()

    def slide_one_step(self) -> None:
        """
        Ends the setup of the slide animation and starts it
        :return: None
        """
        animation = super()._setup_movement_animation()
        animation.bind(on_progress=self._move_selection_circle)
        animation.bind(on_progress=self._move_health_bar)
        self.character.stats.remaining_moves -= 1
        animation.start(self) # change with self.shape if fails

class MonsterToken(CharacterToken):
    """
    Class defining Tokens representing Monsters
    """
    def __init__(self, kind: str, species: str, position: tuple [int,int],
                 character: Monster, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, position, character, dungeon_instance, **kwargs)

    def token_move(self) -> None:
        """
        Initializes the movement of the MonsterToken
        :return: None
        """
        self.path = self.character.move()

        if self.path is None:  # if it cannot move, will try directly to attack players
            self.character.behave(self.get_current_tile())
            self.dungeon.game.update_switch("character_done")
        else:
            self.slide_one_step()

    def token_dodge(self) -> None:
        self.path = self.character.generate_dodge_path()

        if self.path is None:  # dodging failed
            self.get_current_tile().dynamite_fall()
        else:
            self.dodge_one_step()

    def dodge_one_step(self):

        animation = self._setup_dodge_animation()
        animation.start(self)

    def slide_one_step(self) -> None:
        """
        Starts the slide animation
        :return: None
        """
        animation = super()._setup_movement_animation()
        self.character.stats.remaining_moves -= 1
        animation.start(self)

    def _setup_dodge_animation(self):
        next_tile: Tile = self.dungeon.get_tile(self.path.pop(0))
        previous_tile = self.get_current_tile()
        animation = Animation(pos=next_tile.pos, duration=0.2)
        animation.bind(on_complete=lambda animation_obj, token_shape: self.on_dodge_completed(animation,
                                                                                              token_shape,
                                                                                              previous_tile,
                                                                                              next_tile))
        return animation

    def on_dodge_completed(self, animation_obj: Animation, token_shape: Ellipse,
                           previous_tile: Tile, current_tile: Tile) -> None:

        if len(self.path) > 0:
            self.dodge_one_step()
        else:
            self.update_token_on_tile(current_tile)
            previous_tile.dynamite_fall()
