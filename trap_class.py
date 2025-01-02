from __future__ import annotations
from dataclasses import dataclass, field
from random import uniform, randint


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
        damage = self.stats.calculate_damage(self.token.dungeon.dungeon_level)
        damage = player.apply_toughness(damage)

        if player.is_hidden:
            player.unhide()

        player.stats.health -= damage
        player.token.show_damage()
        self.token.show_effect_token(
            "trap", self.token.shape.pos, self.token.shape.size, effect_ends=True  # red
        )
        player.token.bar_length = player.stats.health / player.stats.natural_health

        if player.stats.health <= 0:
            player.kill_character(self.token.get_current_tile())


@dataclass
class TrapStats:
    char: str = "!"
    base_damage: list[int] = field(default_factory=lambda: [1, 6])
    base_experience_when_disarmed: int = 1  #15

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

    def calculate_damage(self, dungeon_level: int) -> int:
        """
        Damage dealt by traps increases with dungeon level
        :param dungeon_level: current level of the dungeon
        :return: damage dealt by the trap
        """
        level: int = dungeon_level // 3
        level = 1 if level < 1 else level
        return randint(self.base_damage[0], self.base_damage[1]) * level

    def calculate_experience(self, dungeon_level: int) -> int:
        """
        Experience granted by traps disarming increases with dungeon level
        :param dungeon_level: current level of the dungeon
        :return: experience rewarded by the trap
        """
        level: int = dungeon_level // 3
        level = 1 if level < 1 else level
        return self.base_experience_when_disarmed * level