from __future__ import annotations
from dataclasses import dataclass, field
from random import randint, uniform

class Trap:

    def __init__(self):
        """
        Class defining Traps
        """
        self.char: str | None = None
        self.kind: str | None = None
        self.species: str | None = None
        self.hidden: bool = True
        self.token: Token | None = None  # initialized in DungeonLayout.place_item()
        self.stats: TrapStats | None = None

    def setup_character(self):
        """
        Placeholder needed by DungeonLayout.match_blueprint()
        """
        pass

    def unhide(self) -> None:
        """
        Unhides the Trap
        :return: None
        """
        self.token.color.a = 1  # changes transparency
        self.hidden = False

    def show_and_damage(self, player: Player) -> None:
        """
        Method controlling the logic of what happens when a trap is stepped on
        :param player: PlayerToken stepping on the trap
        :return:
        """
        self.unhide()
        damage = player.stats.health * uniform(0.0, 1.0)
        damage = player.apply_toughness(damage)

        if player.is_hidden:
            player.unhide()

        player.stats.health -= damage
        player.token.show_damage()
        self.token.show_effect_token(
            "trap", self.token.shape.pos, self.token.shape.size, effect_ends=True  # red
        )

        if player.stats.health <= 0:
            player.kill_character(self.token.get_current_tile())


@dataclass
class TrapStats:
    char: str = "!"
    strength: list[int] = field(default_factory=lambda: [1,3])
    experience_when_killed: int = 5

    @staticmethod
    def calculate_frequency(seed: int) -> float: # seed is level
        # Kobolds decrease with level increase
        if seed < randint(4,7):
            return uniform(0.2, 0.5) / seed
        else:
            return 0