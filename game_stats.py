from dataclasses import dataclass
from abc import ABC
from random import randint


class DungeonStats:

    mandatory_items: tuple[str] = ("%", "?", "&", " ", "o")

    def __init__(self, dungeon_level: int):
        self.stats_level = dungeon_level

    def size(self):

        return 6 + int(self.stats_level * 0.2)

    def gem_number(self):

        gem_number = int(self.stats_level * 0.2)
        gem_number = 1 if gem_number < 1 else gem_number
        return gem_number

    def level_progression(self):

        wall_frequency = randint(2, 6) * 0.1

        monster_frequencies = {
            "K": 0.2 / self.stats_level if self.stats_level < 3 else 0,
            "L": 0.025 * self.stats_level if self.stats_level < 4 else 0,
            "B": randint(0, 3) * 0.02 if self.stats_level > 1 else 0,
            "H": 0.025 * self.stats_level if 2 < self.stats_level < 4 else 0,
            "G": 0.025 * self.stats_level if self.stats_level > 3 else 0,
            "R": 0.015 * self.stats_level if self.stats_level > 4 else 0,
            "O": 0.1 / self.stats_level if self.stats_level < 4 else 0,
            "N": 0.015 * self.stats_level if 3 < self.stats_level < 6 else 0,
            "Y": 0.001 * self.stats_level if 4 < self.stats_level < 8 else 0,
            "S": randint(0, 2) * 0.025,
            "W": 0.05 * self.stats_level if self.stats_level < 3 else 0,
            "D": 0.002 * self.stats_level if 4 < self.stats_level < 8 else 0,
            "P": randint(0, 1) * 0.05,
        }

        total_monster_frequency = sum(monster_frequencies.values())

        item_frequencies = {
            "#": wall_frequency,
            "p": wall_frequency * 0.1,
            "x": total_monster_frequency * 0.15,
            "j": total_monster_frequency * 0.1,
            "c": total_monster_frequency * 0.06,
            "w": total_monster_frequency * 0.06,
            "l": total_monster_frequency * 0.06,
            "t": randint(0, 1) * self.stats_level * 0.02 if self.stats_level > 2 else 0,
            "h": randint(0, 1) * self.stats_level * 0.02,
            "d": randint(0, 1) * self.stats_level * 0.02,
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
    effect_duration: int = 4


@dataclass
class TobaccoStats(ItemStats):
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 4


@dataclass
class WhiskyStats(ItemStats):
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 4


@dataclass
class TalismanStats(ItemStats):
    pass


@dataclass
class CharacterStats(ABC):

    toughness: int = 0
    health: int | None = None
    strength: tuple | None = None
    moves: int | None = None
    remaining_moves: int | None = None

    # needed for players in fight_on_tile()
    experience_when_killed: int | None = None


@dataclass
class PlayerStats(CharacterStats, ABC):

    shovels: int = 2
    digging_moves: int = 1
    weapons: int = 2
    advantage_strength_incr: int | None = None
    shooting_range: int | None = None
    recovery_end_of_level: int = 0  # healthpoints players heal at end of level
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

    random_motility: int = 0  # from 0 to 10. For monsters with random movement

    """
    From 0 to 14. 14 always dodges if at least 1 free tile available nearby. 10 always dodges if 4 free tiles nearby. 0 never dodges. 
    """

    dodging_ability: int = 0
    dodging_moves: int = 2


@dataclass
class SawyerStats(PlayerStats):
    health: int = 6
    strength: list = (1, 2)
    advantage_strength_incr: int = 2
    moves: int = 4
    digging_moves: int = 3


@dataclass
class HawkinsStats(PlayerStats):
    health: int = 8
    strength: list = (1, 3)
    moves: int = 3
    shooting_range: int = 2


@dataclass
class CrusherJaneStats(PlayerStats):
    weapons: int = 4
    health: int = 12
    strength: tuple = (2, 4)
    advantage_strength_incr: int = 1
    moves: int = 3


# RANDOM MOVEMENT MONSTERS


@dataclass
class KoboldStats(MonsterStats):
    health: int = 3
    strength: tuple = (1, 2)
    moves: int = 5
    random_motility: int = 7
    dodging_ability: int = 10
    experience_when_killed: int = 5


@dataclass
class BlindLizardStats(MonsterStats):
    health: int = 5
    strength: tuple = (2, 4)
    moves: int = 5
    random_motility: int = 4
    dodging_ability: int = 3
    experience_when_killed: int = 8


@dataclass
class BlackDeathStats(MonsterStats):
    health: int = 1
    strength: tuple = (10, 15)
    moves: int = 7
    random_motility: int = 10
    dodging_ability: int = 11
    experience_when_killed: int = 30


# DIRECT MOVEMENT MONSTERS


@dataclass
class CaveHoundStats(MonsterStats):
    health: int = 4
    strength: tuple = (1, 3)
    moves: int = 7
    random_motility: int = 8
    dodging_ability: int = 6
    experience_when_killed: int = 10


@dataclass
class GrowlStats(MonsterStats):
    health: int = 10
    strength: tuple = (3, 8)
    moves: int = 5
    random_motility: int = 5
    dodging_ability: int = 3
    experience_when_killed: int = 20


@dataclass
class RockGolemStats(MonsterStats):
    health: int = 40
    strength: tuple = (5, 10)
    moves: int = 3
    dodging_ability: int = 0
    experience_when_killed: int = 45


# SMART MOVEMENT MONSTERS


@dataclass
class DarkGnomeStats(MonsterStats):
    health: int = 2
    strength: tuple = (1, 3)
    moves: int = 5
    random_motility: int = 5
    dodging_ability: int = 14
    experience_when_killed: int = 3


@dataclass
class NightmareStats(MonsterStats):
    health: int = 6
    strength: tuple = (2, 6)
    random_motility: int = 2
    moves: int = 6
    dodging_ability: int = 6
    experience_when_killed: int = 15


@dataclass
class LindWormStats(MonsterStats):
    health: int = 30
    strength: tuple = (12, 18)
    moves: int = 5
    dodging_ability: int = 4
    experience_when_killed: int = 50


# GHOSTS


@dataclass
class WanderingShadowStats(MonsterStats):
    health: int = 2
    strength: tuple = (1, 5)
    moves: int = 8
    random_motility: int = 9
    dodging_ability: int = 14
    experience_when_killed: int = 10


@dataclass
class DepthsWispStats(MonsterStats):
    health: int = 1
    strength: tuple = (1, 2)
    moves: int = 4
    dodging_ability: int = 10
    experience_when_killed: int = 3


@dataclass
class MountainDjinnStats(MonsterStats):
    health: int = 18
    strength: tuple = (5, 10)
    moves: int = 5
    dodging_ability: int = 5
    experience_when_killed: int = 30


# SPECIAL MONSTERS


@dataclass
class PixieStats(MonsterStats):
    health: int = 2
    strength: tuple = (1, 1)
    moves: int = 5
    random_motility: int = 10
    dodging_ability: int = 7
    experience_when_killed: int = 3
