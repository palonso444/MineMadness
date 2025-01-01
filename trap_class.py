from __future__ import annotations
from dataclasses import dataclass, field
from random import randint, uniform

class Trap:

    def __init__(self):
        """
        Class defining Traps
        """
        self.char: str | None = "!"
        self.kind: str | None = "trap"
        self.species: str | None = "trap"
        self.hidden: bool = True
        self.token: Token | None = None  # initialized in DungeonLayout.place_item()
        self.stats: TrapStats | None = TrapStats()

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
        damage = self.stats.calculate_damage(player)
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
    experience_when_killed: int = 5

    @staticmethod
    def calculate_frequency(seed: int) -> float: # seed is level
        # Traps start showing late and increase frequency with increasing level
        if seed < 5:
            return 0
        if seed < 10:
            return uniform(0, 0.15)
        if seed < 15:
            return uniform(0, 0.2)
        if seed < 20:
            return uniform(0.05, 0.3)
        else:
            return uniform(0.1, 0.4)

    @staticmethod
    def calculate_damage(player: Player) -> int:
        return player.stats.health * uniform(0.0, 1.0)