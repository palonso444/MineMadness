from dataclasses import dataclass
from abc import ABC
from random import randint


class DungeonStats:

    mandatory_items: tuple[str] = ("%", "?", "&", " ", "o")

    def __init__(self, dungeon_level: int):
        self.level = dungeon_level

    def size(self):

        # return 6 + int(self.level / 1.5)
        return 4 * self.level

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
    effect_duration: int = 1


@dataclass
class TobaccoStats(ItemStats):
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 1


@dataclass
class WhiskyStats(ItemStats):
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 1


@dataclass
class TalismanStats(ItemStats):
    pass


@dataclass
class CharacterStats(ABC):

    thoughness: int = 0
    health: int | None = None
    strength: tuple | None = None
    moves: int | None = None
    remaining_moves: int | None = None


@dataclass
class PlayerStats(CharacterStats, ABC):

    shovels: int = 2
    digging_moves: int = 1
    weapons: int = 5
    advantage_strength_incr: int | None = None
    shooting_range: int | None = None
    recovery_end_of_level: int = 100  # healthpoints players heal at end of level
    base_exp_to_level_up: int = 10

    def __post_init__(self):
        self.natural_health: int = self.health  # only modified by leveling up
        self.natural_moves: int = self.moves  # only modified by leveling up
        self.natural_strength: tuple = self.strength  # only modified by leveling up
        self.exp_to_next_level: int = self.base_exp_to_level_up


@dataclass
class MonsterStats(CharacterStats, ABC):
    """
    From 0 to 10. 10 always mobile, 0 immobile. For monsters with random movement
    """

    random_motility: int = 0

    """
    From 0 to 14. 14 always dodges if at least 1 free tile available nearby. 10 always dodges if 4 free tiles nearby. 0 never dodges. 
    """

    dodging_ability: int = 0

    experiece_when_killed: int = 5


@dataclass
class SawyerStats(PlayerStats):
    health: int = 50
    strength: list = (1, 2)
    advantage_strength_incr: int = 100
    moves: int = 4
    digging_moves: int = 3


@dataclass
class HawkinsStats(PlayerStats):
    health: int = 50
    strength: list = (1, 4)
    moves: int = 4
    shooting_range: int = 2


@dataclass
class CrusherJaneStats(PlayerStats):
    health: int = 50
    strength: tuple = (3, 6)
    advantage_strength_incr: int = 100
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
    moves: int = 4
    random_motility: int = 8
    dodging_ability: int = 10


@dataclass
class DepthsWispStats(MonsterStats):
    health: int = 1
    strength: tuple = (1, 2)
    moves: int = 5
    random_motility: int = 5
    dodging_ability: int = 10


@dataclass
class NightmareStats(MonsterStats):
    health: int = 6
    strength: tuple = (2, 5)
    moves: int = 4
    dodging_ability: int = 10


@dataclass
class GreedyGnomeStats(MonsterStats):
    health: int = 6
    strength: tuple = (1, 3)
    moves: int = 5
    random_motility: int = 6  # from 0 to 10. For monsters with random movement
