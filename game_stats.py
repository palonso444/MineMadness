from dataclasses import dataclass
from abc import ABC


@dataclass
class CharacterStats(ABC):

    health: int | None = None
    remaining_moves: int | None = None

    def __post_init__(self):
        self.max_health = self.health


@dataclass
class PlayerStats(CharacterStats, ABC):

    health: int | None = None
    shovels: int = 0
    digging_moves: int = 1
    weapons: int = 0
    armed_strength_incr: int | None = None


@dataclass
class MonsterStats(CharacterStats, ABC):

    random_motility: int = 0  # from 0 to 10. For monsters with random movement


@dataclass
class SawyerStats(PlayerStats):
    health: int = 400
    strength: tuple = (1, 2)
    moves: int = 5
    digging_moves: int = 3


@dataclass
class HawkinsStats(PlayerStats):
    health: int = 5
    strength: tuple = (1, 4)
    moves: int = 4


@dataclass
class CrusherJaneStats(PlayerStats):
    health: int = 80
    strength: tuple = (3, 6)
    armed_strength_incr: int = 2
    moves: int = 3


@dataclass
class KoboldStats(MonsterStats):
    health: int = 2
    strength: tuple = (1, 2)
    moves: int = 3
    random_motility: int = 8


@dataclass
class CaveHoundStats(MonsterStats):
    health: int = 4
    strength: tuple = (1, 4)
    moves: int = 2
    random_motility: int = 8


@dataclass
class DepthsWispStats(MonsterStats):
    health: int = 1
    strength: tuple = (1, 2)
    moves: int = 5
    random_motility: int = 5


@dataclass
class NightmareStats(MonsterStats):
    health: int = 6
    strength: tuple = (2, 5)
    moves: int = 15
