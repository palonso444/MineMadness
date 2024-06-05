from dataclasses import dataclass
from abc import ABC
from random import randint

# from kivy.event import EventDispatcher
# from kivy.properties import NumericProperty


class DungeonStats:  # inherit from EventDispatcher to use NumericProperty

    mandatory_items: tuple[str] = ("%", "?", "&", " ", "o")

    # level: int = NumericProperty(1)

    def __init__(self):
        self.level: int = 1

    def size(self):

        return 6 + int(self.level / 1.5)

    def gem_number(self):

        gem_number = int(self.level * 0.2)
        gem_number = 1 if gem_number < 1 else gem_number
        return gem_number

    def level_progression(self):

        wall_frequency = randint(20, 60) * 0.01

        monster_frequencies = {
            "K": 0.10 / self.level,
            "H": self.level * 0.015,
            "W": self.level * 0.006,
            "N": self.level * 0.002,
        }

        total_monster_frequency = sum(monster_frequencies.values())

        item_frequencies = {
            "#": wall_frequency,
            "p": wall_frequency * 0.15,
            "x": total_monster_frequency * 0.3,
            "j": self.level * 0.015,
        }

        all_frequencies = {**monster_frequencies, **item_frequencies}

        del monster_frequencies, item_frequencies
        return all_frequencies


@dataclass
class ItemStats(ABC):
    effect_size: float | None = None
    effect_duration: int | None = None
    use_time: int = 1
    min_effect: int = 1
    max_effect: int | None = None


@dataclass
class JerkyStats(ItemStats):
    effect_size: float = 0.3  # percentage of increase respect character stats
    min_effect: int = 2


@dataclass
class CoffeeStats(ItemStats):
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 3


@dataclass
class TobaccoStats(ItemStats):
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 3


@dataclass
class WhiskyStats(ItemStats):
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 4


@dataclass
class CharacterStats(ABC):

    thoughness: int = 0
    health: int | None = None
    strength: tuple | None = None
    moves: int | None = None
    remaining_moves: int | None = None


@dataclass
class PlayerStats(CharacterStats, ABC):

    shovels: int = 0
    digging_moves: int = 1
    weapons: int = 0
    armed_strength_incr: int | None = None

    def __post_init__(self):
        self.max_health: int = self.health  # only modified by leveling up
        self.natural_moves: int = self.moves  # only modified by leveling up
        self.natural_strength: tuple = self.strength  # only modified by leveling up


@dataclass
class MonsterStats(CharacterStats, ABC):

    random_motility: int = 0  # from 0 to 10. For monsters with random movement


@dataclass
class SawyerStats(PlayerStats):
    health: int = 400
    strength: list = (1, 2)  # TODO: list as it may vary
    moves: int = 5
    digging_moves: int = 3


@dataclass
class HawkinsStats(PlayerStats):
    health: int = 5
    strength: list = (1, 4)  # TODO: list as it may vary
    moves: int = 4


@dataclass
class CrusherJaneStats(PlayerStats):
    health: int = 10
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


@dataclass
class GreedyGnomeStats(MonsterStats):
    health: int = 6
    strength: tuple = (1, 3)
    moves: int = 5
    random_motility: int = 6  # from 0 to 10. For monsters with random movement
