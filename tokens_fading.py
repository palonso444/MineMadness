from __future__ import annotations
from abc import ABC, ABCMeta
from kivy.graphics import Ellipse, Rectangle, Color, Line  # type: ignore
from kivy.animation import Animation
from kivy.uix.widget import Widget


class WidgetABCMeta(ABCMeta,type(Widget)):
    """
    Base metaclass allowing to make FadingToken an abstract class (otherwise there is conflict because inherits from
    Widget, so it cannot inherit from ABC inherently)
    """
    pass

class FadingToken(Widget, ABC, metaclass=WidgetABCMeta):
    """
    Base abstract class defining all Tokens that fade in and out without remaining on the board
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0  # FadingTokens start invisible. None is not allowed
        self.final_opacity: int | None = None
        self.duration: int | None = None

    def fade(self) -> None:
        """
        Handles the fading (in and out) of the FadingToken
        :return: None
        """
        fading = Animation(opacity=self.final_opacity, duration=self.duration)
        fading.bind(on_complete=self._fade_out)
        fading.start(self)

    @staticmethod
    def _fade_out(animation: Animation, token: FadingToken) -> None:
        """
        Handles the fading out of the FadingToken
        :param animation: fade Animation object
        :param token: FadingToken which is about to fade out
        :return: None
        """
        fading_out = Animation(opacity=0, duration=token.duration)
        if isinstance(token, EffectToken):
            # token.character_token is the CharacterToken upon which FadingToken acts
            fading_out.bind(on_complete=token.character_token.remove_effect_if_in_queue)
        # game_already_over avoids interferences of game_over screens if massive killing:
        elif isinstance(token, DamageToken) and not token.game.game_already_over:
            fading_out.bind(on_complete=token.game.check_if_game_over)
        fading_out.start(token)


class DamageToken(FadingToken):
    """
    Class defining the FadingTokens representing damage
    """
    def __init__(self, pos: tuple[float,float], size: tuple[float,float],
                 game: MineMadnessGame, **kwargs):
        super().__init__(**kwargs)
        self.final_opacity = 0.25
        self.duration = 0.2
        self.game: MineMadnessGame = game

        with self.canvas:
            self.color = Color(1, 0, 0, 1)
            self.shape = Ellipse(pos=pos, size=size)

        self.fade()


class DiggingToken(FadingToken):
    """
    Class defining the FadingTokens representing digging
    """
    def __init__(self, pos:tuple[float,float], size:tuple[float,float], **kwargs):
        super().__init__(**kwargs)
        self.final_opacity = 0.7
        self.duration = 0.2

        with self.canvas:
            self.color = Color(0.58, 0.294, 0, 1)
            self.shape = Rectangle(pos=pos, size=size)

        self.fade()


class ExplosionToken(FadingToken):
    """
    Class defining the FadingTokens representing explosions
    """

    def __init__(self, pos: tuple[float,float], size: tuple[float,float], **kwargs):
        super().__init__(**kwargs)
        self.final_opacity = 0.7
        self.duration = 0.2
        self.source = "./fadingtokens/explosion_token.png"

        with self.canvas:
            self.color = Color(1, 1, 1, 1)
            self.shape = Rectangle(pos=pos, size=size, source=self.source)

        self.fade()


class EffectToken(FadingToken):
    """
    Class defining the FadingTokens representing effects on Character attributes (moves, strength, etc.)
    """
    def __init__(self, pos: tuple[float,float], size: tuple[float,float], effect: str,
                 character_token: CharacterToken, effect_ends: bool, **kwargs):
        super().__init__(**kwargs)
        self.final_opacity = 1
        self.duration = 0.6
        self.effect = effect
        self.character_token: CharacterToken = character_token
        self.effect_ends: bool = effect_ends  # determines if effect start or ends

        if effect_ends:
            self.source = f"./fadingtokens/{self.effect}_effect_red_token.png"
        else:
            self.source = f"./fadingtokens/{self.effect}_effect_green_token.png"

        with self.canvas:
            self.color = Color(1, 1, 1, 1)
            self.shape = Rectangle(pos=pos, size=size, source=self.source)

        self.fade()
