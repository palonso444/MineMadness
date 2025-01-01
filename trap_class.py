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