from __future__ import annotations
from abc import ABC, ABCMeta

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
                 character: Character, dungeon_instance: DungeonLayout,
                 size_modifier: float, pos_modifier: tuple[int,int], **kwargs):
        super().__init__(**kwargs)

        self.kind: str = kind
        self.species: str = species
        self.position: tuple [int:int] = position
        self.character: Character = character
        self.dungeon: DungeonLayout = dungeon_instance
        self.source: str = "./tokens/" + self.species + "token.png"
        self.shape: Ellipse | Rectangle | None = None  # token.shape (canvas object) initialized in each subclass

        # size and pos attributes comes from the superclass
        self.pos_modifier: [tuple[float,float]] = pos_modifier
        self.size_modifier: float = size_modifier
        self.size: [tuple[float,float]] = self.size[0] * size_modifier, self.size[1] * size_modifier
        self.pos: [tuple[float, float]] = self.pos[0] + pos_modifier[0], self.pos[1] - pos_modifier[1]  # (x,y)

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
        if self.shape in self.dungeon.canvas.children:
            self.dungeon.canvas.remove(self.shape)
        elif self.shape in self.dungeon.canvas.after.children:  # walls are in canvas after
            self.dungeon.canvas.after.remove(self.shape)
        if self.character is not None:
            self.character.token = None

class SceneryToken(SolidToken):
    """
    Base class defining Tokens without associated Character
    """
    def __init__(self, kind: str, species: str, position: tuple[int,int],
                 character: None, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, position, character, dungeon_instance, **kwargs)

        if self.kind in ["wall", "light"]:
            canvas_context = self.dungeon.canvas.after
        else:
            canvas_context = self.dungeon.canvas

        with canvas_context:
            self.color = Color(1, 1, 1, 1)
            self.shape = Rectangle(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update_pos)

    def show_digging(self) -> None:
        """
        Shows the on the Token the FadingToken corresponding to the digging action of a Player
        :return: None
        """
        with self.dungeon.canvas:
            DiggingToken(pos=self.pos, size=self.size)


class CharacterToken(SolidToken, ABC, metaclass=WidgetABCMeta):
    """
    Base abstract class defining all Tokens with associated Character. It represents all the aspects related
    to their physical representation on the board (picture, position, health bar(if applicable)),
    showing of EffectTokens and movement.
    """

    def __init__(self, kind: str, species: str, position: tuple[int,int], character: Character,
                 dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, position, character, dungeon_instance, **kwargs)

        self.start_position: tuple[int,int] | None = None
        self.path: list[tuple[int,int]] | None = None
        self.color: tuple[int,int,int,int]| None = None
        self._display_in_canvas()

    def _display_in_canvas(self) -> None:
        """
        Displays CharacterToken.shape on the canvas of the DungeonLayout
        :return: None
        """
        with self.dungeon.canvas:
            if self.character.is_hidden:
                self.color = Color(1, 1, 1, self.color.a)
            else:
                self.color = Color(1, 1, 1, 1)
            self.shape = Ellipse(pos=self.pos, size=self.size, source=self.source)

        self.bind(pos=self.update_pos)

    def select_character(self) -> None:
        """
        Resets the display of CharacterToken.shape it ends up in the upper layer of the canvas
        :return: None
        """
        self.dungeon.canvas.remove(self.shape)
        self._display_in_canvas()

    def unselect_token(self) -> None:
        """
        Placeholder. MonsterToken do not have selection circle but this function is called in MineMadnessGame
        :return: None
        """
        pass

    def _move_selection_circle(self, *args) -> None:
        """
        Placeholder. Monsters do not have selection circle but this is necessary for the functioning of
        CharacterToken._slide_one_step()
        :param args: This function receives variable number of arguments. They cannot be typehint
        :return: None
        """
        pass

    def _move_health_bar(self, *args) -> None:
        """
        Placeholder. Monsters do not have health bar but this is necessary for the functioning of
        CharacterToken._slide_one_step()
        :param args: This function receives variable number of arguments. They cannot be typehint
        :return: None
        """
        pass

    def update_token_on_tile(self, tile : Tile) -> None:
        """
        Updates all necessary parameters when a CharacterToken lands on a new Tile
        :param tile: Tile in which the Token has landed
        :return: None
        """
        tile.set_token(self)
        self.position = tile.position
        self.pos: tuple[int, int] = self.shape.pos
        self.path: list[tuple[int, int]] | None = None

    def slide(self, path: list [tuple[int,int]],
                    on_complete: Callable[[Animation, Ellipse, Tile, Callable], None]) -> None:
        """
        Initializes the movement of the CharacterToken.
        :param path: list of coordinates that mark the path that the CharacterToken will follow.
        :param on_complete: callback to be triggered once the path is completed or the character runs out of moves
        :return: None
        """
        self.get_current_tile().remove_token(self)
        self.start_position = path[0]
        self.path = path[1:]
        self.dungeon.disable_all_tiles()
        self._slide_one_step(on_complete)

    def _slide_one_step(self, on_complete: Callable) -> None:
        """
        Starts the animation of the CharacterToken sliding one step on CharacterToken.path
        :param on_complete: callback to be triggered once the path is completed or the character runs out of moves
        :return: None
        """
        next_tile: Tile = self.dungeon.get_tile(self.path.pop(0))

        animation = Animation(pos=next_tile.pos, duration=self.character.step_duration,
                              transition=self.character.step_transition)

        animation.bind(on_complete=lambda animation_obj, token_shape: on_complete(animation_obj,
                                                                               token_shape,
                                                                               next_tile,
                                                                               on_complete))
        animation.bind(on_progress=self._move_selection_circle)
        animation.bind(on_progress=self._move_health_bar)
        animation.start(self)

    def on_move_completed(self, animation_obj: Animation,
                           token_shape: Ellipse,
                           current_tile: Tile,
                           on_complete: Callable) -> None:
        """
        Callback triggered when a slide step of a CharacterToken in its turn is completed
        :param animation_obj: animation object taking care of sliding the CharacterToken
        :param token_shape: shape of the CharacterToken
        :param current_tile: current Tile in which the CharacterToken is located
        :param on_complete: callback to be triggered once the path is completed or the character runs out of moves
        :return: None
        """
        self.character.stats.remaining_moves -= 1
        if len(self.path) > 0:
            self._slide_one_step(on_complete)
        else:
            self.update_token_on_tile(current_tile)
            self.character.act_on_tile(current_tile)

    def show_damage(self) -> None:
        """
        Shows the on the Token the FadingToken corresponding to damage
        :return: None
        """
        with self.dungeon.canvas.after:  # canvas.after to ensure is visible on the CharacterToken
            DamageToken(pos=self.pos, size=self.size)


class PlayerToken(CharacterToken):
    """
    Class defining Tokens representing Players
    """
    bar_length = NumericProperty(None)
    modified_attributes = ListProperty([])

    def __init__(self, kind: str, species: str, character: Player, position: tuple[int,int],
                 dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, position, character, dungeon_instance, **kwargs)

        self.circle: Line | None = None
        self.circle_color: Line | None = None
        self.green_bar: Rectangle | None = None
        self.red_bar: Rectangle | None = None

        self.bind(bar_length=self._display_health_bar)
        self.post_init()

    def post_init(self) -> None:
        """
        Changes the value of remaining_health to initialize health bar
        :return: None
        """
        self.bar_length = (
                self.character.stats.health / self.character.stats.natural_health
        )

    def select_character(self) -> None:
        """
        Resets the display of CharacterToken.shape and associated circle and health bar so they end up in the upper
        layer of the canvas
        :return: None
        """
        super().select_character()
        self._display_health_bar(self, self.bar_length)
        self._display_selection_circle()

    @staticmethod
    def on_modified_attributes(character_token: CharacterToken, modified_attributes: list[str]) -> None:
        """
        Shows FadingTokens for the effect modifying the next attribute on the queue
        :param character_token: CharacterToken on which FadingToken is shown
        :param modified_attributes: queue of currently modified attributes
        :return: None
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
                          size: tuple [float,float], effect_ends: bool = False) -> None:
        """
        Shows the FadingToken of the effect modifying the specified character attribute
        :param attribute: attribute being modified
        :param pos: position of (on the screen) of the CharacterToken that shows the FadingToken
        :param size: size of the CharacterToken that shows the FadingToken
        :param effect_ends: specifies if the effect ends (red FadingToken) of begins (green FadingToken)
        :return: None
        """
        with self.dungeon.canvas.after:
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
        token._restart_health_bar()

        bar_pos_x = token.pos[0] + (token.size[0] * 0.1)
        bar_pos_y = token.pos[1] + (token.size[1] * 0.1)
        bar_length = token.size[0] * 0.8  # total horizontal length of the bar
        bar_thickness = token.size[1] * 0.1

        with token.dungeon.canvas:
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

    def _restart_health_bar(self) -> None:
        """
        Removes the health bar, if present. Call this instead of Token._remove_health_bar() to avoid error if bar not
        present
        :return: None
        """
        if self.green_bar is not None and self.red_bar is not None:
            self._remove_health_bar()

    def _remove_health_bar(self) -> None:
        """
        Removes the health bar
        :return: None
        """
        self.dungeon.canvas.remove(self.green_bar)
        self.dungeon.canvas.remove(self.red_bar)
        self.green_bar = None
        self.red_bar = None

    def _display_selection_circle(self) -> None:
        """
        Displays the selection circle around the selected CharacterToken
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

    def unselect_token(self) -> None:
        """
        Removes the selection circle from the Token, if present. Call this instead of Token._remove_selection_circle()
        to avoid error if circle not present
        :return: None
        """
        if self.circle is not None:
            self._remove_selection_circle()

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

    def _remove_selection_circle(self) -> None:
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
        self.unselect_token()
        self._remove_health_bar()


class MonsterToken(CharacterToken):
    """
    Class defining Tokens representing Monsters
    """
    def __init__(self, kind: str, species: str, position: tuple [int,int],
                 character: Monster, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(kind, species, position, character, dungeon_instance, **kwargs)


    def on_dodge_completed(self, animation_obj: Animation, token_shape: Ellipse,
                           current_tile: Tile, on_complete: Callable) -> None:
        """
        Callback triggered when a slide step of a MonsterToken outside turn is completed
        :param animation_obj: animation object taking care of sliding the MonsterToken
        :param token_shape: shape of the MonsterToken
        :param current_tile: current Tile in which the MonsterToken is located
        :param on_complete: callback to be triggered once the path is completed or the monster runs out of moves
        :return: None
        """
        if len(self.path) > 0:
            self._slide_one_step(on_complete)
        else:
            self.update_token_on_tile(current_tile)
