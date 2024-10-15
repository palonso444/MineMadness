from __future__ import annotations
from kivy.graphics import Ellipse, Rectangle, Color, Line  # type: ignore
from kivy.animation import Animation

from kivy.uix.widget import Widget


class FadingToken(Widget):

    def __init__(self, character_token: CharacterToken, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.final_opacity = None
        self.character_token: CharacterToken = character_token
        self.duration: int | None = None

    def fade(self):

        def fade_out(*args):

            fading_out = Animation(opacity=0, duration=self.duration)
            if isinstance(self, EffectToken):
                fading_out.bind(on_complete=self.character_token.remove_attribute_if_in_queue)
            fading_out.start(self)

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

    def __init__(self, item: str, character_token, effect_ends: bool, **kwargs):
        super().__init__(character_token, **kwargs)
        self.final_opacity = 1
        self.duration = 0.6
        self.item = item
        self.effect_ends: bool = effect_ends

        if effect_ends:
            self.source = "./fadingtokens/" + self.item + "_fades_token.png"
        else:
            self.source = "./fadingtokens/" + self.item + "_effect_token.png"

        with self.canvas:
            self.shape = Rectangle(pos=self.pos, size=self.size, source=self.source)

        self.fade()