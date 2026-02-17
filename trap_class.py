from __future__ import annotations
from game_stats import TrapStats

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

    @property
    def is_hidden(self) -> bool:
        """
        Property defining if the trap is hidden
        :return: True if the trap is hidden, False otherwise
        """
        return self.hidden

    def setup_character(self, game: MineMadnessGame):
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
        :return: None
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
