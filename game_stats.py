from dataclasses import dataclass, field
from abc import ABC
from random import randint, uniform, random


class DungeonStats:

    mandatory_items: tuple[str,str,str,str,str] = ("%", "?", "&", " ", "o")

    def __init__(self, dungeon_level: int):
        self.stats_level = dungeon_level

    def size(self) -> int:
        return 6 + int(self.stats_level * 0.2)

    def gem_number(self) -> int:

        gem_number = int(self.stats_level * 0.15)
        gem_number = 1 if gem_number < 1 else gem_number
        return gem_number

    def level_progression(self) -> dict[str:float]:
        """
        Organizes in a dictionary the frequency of items in the level
        :return: dictionary with item.char as key and item frequency as value
        """
        monster_frequencies = {
            KoboldStats.char: KoboldStats.calculate_frequency(self.stats_level),
            BlindLizardStats.char: BlindLizardStats.calculate_frequency(self.stats_level),
            BlackDeathStats.char: BlackDeathStats.calculate_frequency(self.stats_level),
            CaveHoundStats.char: CaveHoundStats.calculate_frequency(self.stats_level),
            GrowlStats.char: GrowlStats.calculate_frequency(self.stats_level),
            RockGolemStats.char: RockGolemStats.calculate_frequency(self.stats_level),
            DarkGnomeStats.char: DarkGnomeStats.calculate_frequency(self.stats_level),
            NightmareStats.char: NightmareStats.calculate_frequency(self.stats_level),
            LindWormStats.char: LindWormStats.calculate_frequency(self.stats_level),
            WanderingShadowStats.char: WanderingShadowStats.calculate_frequency(self.stats_level),
            DepthsWispStats.char: DepthsWispStats.calculate_frequency(self.stats_level),
            MountainDjinnStats.char: MountainDjinnStats.calculate_frequency(self.stats_level),
            PixieStats.char: PixieStats.calculate_frequency(self.stats_level),
        }

        total_monster_frequency = sum(monster_frequencies.values())

        rock_wall_frequency = RockWallStats.calculate_frequency(self.stats_level)
        granite_wall_frequency = GraniteWallStats.calculate_frequency(self.stats_level)
        diggable_wall_frequency = rock_wall_frequency + granite_wall_frequency

        '''item_frequencies = {
            RockWallStats.char: rock_wall_frequency,
            GraniteWallStats.char: granite_wall_frequency,
            QuartzWallStats.char: QuartzWallStats.calculate_frequency(self.stats_level),
            ShovelStats.char: ShovelStats.calculate_frequency(diggable_wall_frequency),
            WeaponStats.char: WeaponStats.calculate_frequency(total_monster_frequency),
            JerkyStats.char: JerkyStats.calculate_frequency(total_monster_frequency),
            CoffeeStats.char: CoffeeStats.calculate_frequency(total_monster_frequency),
            WhiskyStats.char: WhiskyStats.calculate_frequency(total_monster_frequency),
            TobaccoStats.char: TobaccoStats.calculate_frequency(total_monster_frequency),
            TalismanStats.char: TalismanStats.calculate_frequency(self.stats_level),
            PowderStats.char: PowderStats.calculate_frequency(self.stats_level),
            DynamiteStats.char: DynamiteStats.calculate_frequency(self.stats_level)
        }'''

        item_frequencies = {
            ShovelStats.char: ShovelStats.calculate_frequency(diggable_wall_frequency),
            WeaponStats.char: WeaponStats.calculate_frequency(total_monster_frequency),
            JerkyStats.char: JerkyStats.calculate_frequency(total_monster_frequency),
            CoffeeStats.char: CoffeeStats.calculate_frequency(total_monster_frequency),
            WhiskyStats.char: WhiskyStats.calculate_frequency(total_monster_frequency),
            TobaccoStats.char: TobaccoStats.calculate_frequency(total_monster_frequency),
            TalismanStats.char: TalismanStats.calculate_frequency(self.stats_level)
        }

        all_frequencies = {**monster_frequencies, **item_frequencies}
        return item_frequencies
        del monster_frequencies, item_frequencies

        #return all_frequencies

@dataclass
class SceneryStats(ABC):
    char: str | None = None

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:
        pass


class RockWallStats(SceneryStats): # DONE
    char: str = "#"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        if seed < randint (6, 9):
            return uniform(0.2, 0.7)
        if randint(1, 10) < 5:
            return uniform(0, 0.2)
        else:
            upper_limit = seed * 0.04
            return uniform(0.1, upper_limit) if seed < 18 else uniform(0.1, 0.7)


class GraniteWallStats(SceneryStats): # DONE
    char: str = "{"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        if seed < randint (6, 9):
            return 0
        if randint(1, 10) < 5:
            return uniform(0, 0.2)
        else:
            upper_limit = seed * 0.03
            return uniform(0, upper_limit) if seed < 16 else uniform(0, 0.5)


class QuartzWallStats(SceneryStats): # DONE
    char: str = "*"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        if seed < randint(10, 15):
            return 0
        if randint(1, 10) < 5:
            return uniform(0, 0.15)
        else:
            upper_limit = seed * 0.02
            return uniform(0, upper_limit) if seed < 18 else uniform(0, 0.4)


class ShovelStats(SceneryStats): # DONE
    char: str = "p"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is diggable wall frequency
        upper_limit = seed * 0.1
        frequency =  uniform(0, upper_limit) - uniform(0,upper_limit)
        return frequency if frequency > 0 else 0


class WeaponStats(SceneryStats): #DONE
    char: str = "x"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is monster frequency
        upper_limit = seed * 0.3
        frequency =  uniform(0, upper_limit) - uniform(0, upper_limit)
        return frequency if frequency > 0 else 0


class PowderStats(SceneryStats): # DONE
    char: str = "h"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is level
        if randint(1, 10) < 4 or seed < 3:
            return 0
        else:
            upper_limit = seed * 0.03 if seed < 15 else 0.5
            frequency = uniform(0, upper_limit) - uniform(0, upper_limit)
            return frequency if frequency > 0 else 0


class DynamiteStats(SceneryStats): # DONE
    char: str = "d"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is level
        if randint(1, 10) < 4 or seed < 3:
            return 0
        else:
            upper_limit = seed * 0.03 if seed < 15 else 0.5
            frequency = uniform(0, upper_limit) - uniform(0, upper_limit)
            return frequency if frequency > 0 else 0



@dataclass
class ItemStats(SceneryStats, ABC):
    effect_size: float | None = None
    effect_duration: int | None = None
    use_time: int = 1
    min_effect: int = 1
    max_effect: int | None = None


@dataclass
class JerkyStats(ItemStats):  # DONE
    char: str = "j"
    effect_size: float = 0.3  # percentage of increase respect character stats
    min_effect: int = 2

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is monster frequency
        frequency = uniform(0, seed) - uniform(0, seed)
        return frequency if frequency > 0 else 0


@dataclass
class CoffeeStats(ItemStats):  # DONE
    char: str = "c"
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 3

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is monster frequency
        frequency = uniform(0, seed) - uniform(0, seed)
        return frequency if frequency > 0 else 0


@dataclass
class TobaccoStats(ItemStats):  # DONE
    char: str = "l"
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 3

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is monster frequency
        frequency = uniform(0, seed) - uniform(0, seed)
        return frequency if frequency > 0 else 0


@dataclass
class WhiskyStats(ItemStats):  # DONE
    char: str = "w"
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 3

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is monster frequency
        frequency = uniform(0, seed) - uniform(0, seed)
        return frequency if frequency > 0 else 0


@dataclass
class TalismanStats(ItemStats): # DONE
    char: str = "t"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is level
        if randint(1, 10) < 5 or seed < randint(6,15):
            return 0
        else:
            frequency = uniform(0, seed * 0.3) - uniform(0, seed * 0.3)
            return frequency if frequency > 0 else 0


@dataclass
class CharacterStats(ABC):

    toughness: int = 0
    health: int | None = None
    strength: list[int] | None = None
    moves: int | None = None
    remaining_moves: int | None = None

    # needed for players in fight_on_tile()
    experience_when_killed: int | None = None

    def to_dict(self) -> dict:
        return {key:value for key, value in vars(self).items()}

    def overwrite_attributes(self, attributes_dict: dict) -> None:

        for attribute, value in attributes_dict.items():
            setattr(self, attribute, value)


@dataclass
class PlayerStats(CharacterStats, ABC):

    shovels: int = 2
    digging_moves: int = 1
    weapons: int = 2
    advantage_strength_incr: int | None = None
    shooting_range: int | None = None
    recovery_end_of_level: int = 0  # health points players heal at end of level
    base_exp_to_level_up: int = 10

    def __post_init__(self):
        self.natural_health: int = self.health  # only modified by leveling up
        self.natural_moves: int = self.moves  # only modified by leveling up
        self.natural_strength: list[int] = self.strength  # only modified by leveling up
        self.exp_to_next_level: int = self.base_exp_to_level_up


@dataclass
class SawyerStats(PlayerStats):
    health: int = 6
    strength: list[int] = field(default_factory=lambda: [1,2])
    advantage_strength_incr: int = 2
    moves: int = 4
    digging_moves: int = 3


@dataclass
class HawkinsStats(PlayerStats):
    health: int = 8
    strength: list[int] = field(default_factory=lambda: [1,3])
    moves: int = 3
    shooting_range: int = 2


@dataclass
class CrusherJaneStats(PlayerStats):
    weapons: int = 4
    health: int = 12
    strength: list[int] = field(default_factory=lambda: [2,4])
    advantage_strength_incr: int = 1
    moves: int = 3


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

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        pass


# RANDOM MOVEMENT MONSTERS


@dataclass
class KoboldStats(MonsterStats):
    char: str = "K"
    health: int = 3
    strength: list[int] = field(default_factory=lambda: [1,2])
    moves: int = 5
    random_motility: int = 7
    dodging_ability: int = 0
    experience_when_killed: int = 5

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.2 / seed if seed < 3 else 0


@dataclass
class BlindLizardStats(MonsterStats):
    char: str = "L"
    health: int = 5
    strength: list[int] = field(default_factory=lambda: [2,4])
    moves: int = 5
    random_motility: int = 4
    dodging_ability: int = 3
    experience_when_killed: int = 8

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.025 * seed if seed < 4 else 0


@dataclass
class BlackDeathStats(MonsterStats):
    char: str = "B"
    health: int = 1
    strength: list[int] = field(default_factory=lambda: [10,20])
    moves: int = 7
    random_motility: int = 10
    dodging_ability: int = 11
    experience_when_killed: int = 30

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return randint(0, 3) * 0.02 if seed > 1 else 0


# DIRECT MOVEMENT MONSTERS


@dataclass
class CaveHoundStats(MonsterStats):
    char: str = "H"
    health: int = 4
    strength: list[int] = field(default_factory=lambda: [1,4])
    moves: int = 7
    random_motility: int = 8
    dodging_ability: int = 6
    experience_when_killed: int = 10

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.025 * seed if 2 < seed < 4 else 0


@dataclass
class GrowlStats(MonsterStats):
    char: str = "G"
    health: int = 10
    strength: list[int] = field(default_factory=lambda: [5,15])
    moves: int = 5
    random_motility: int = 5
    dodging_ability: int = 3
    experience_when_killed: int = 20

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.025 * seed if seed > 3 else 0


@dataclass
class RockGolemStats(MonsterStats):
    char: str = "R"
    health: int = 50
    strength: list[int] = field(default_factory=lambda: [5,20])
    moves: int = 3
    dodging_ability: int = 0
    experience_when_killed: int = 45

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.015 * seed if seed > 4 else 0


# SMART MOVEMENT MONSTERS


@dataclass
class DarkGnomeStats(MonsterStats):
    char: str = "O"
    health: int = 2
    strength: list[int] = field(default_factory=lambda: [1,3])
    moves: int = 5
    random_motility: int = 5
    dodging_ability: int = 14
    experience_when_killed: int = 3

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.1 / seed if seed < 4 else 0


@dataclass
class NightmareStats(MonsterStats):
    char: str = "N"
    health: int = 6
    strength: list[int] = field(default_factory=lambda: [2,6])
    random_motility: int = 2
    moves: int = 6
    dodging_ability: int = 6
    experience_when_killed: int = 15

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.015 * seed if 3 < seed < 6 else 0


@dataclass
class LindWormStats(MonsterStats):
    char: str = "Y"
    health: int = 30
    strength: list[int] = field(default_factory=lambda: [20,35])
    moves: int = 5
    dodging_ability: int = 4
    experience_when_killed: int = 50

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.001 * seed if 4 < seed < 8 else 0


# GHOSTS


@dataclass
class WanderingShadowStats(MonsterStats):
    char: str = "S"
    health: int = 2
    strength: list[int] = field(default_factory=lambda: [1,5])
    moves: int = 8
    random_motility: int = 9
    dodging_ability: int = 14
    experience_when_killed: int = 10

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return randint(0, 2) * 0.025


@dataclass
class DepthsWispStats(MonsterStats):
    char: str = "W"
    health: int = 1
    strength: list[int] = field(default_factory=lambda: [1,2])
    moves: int = 4
    dodging_ability: int = 10
    experience_when_killed: int = 3

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.05 * seed if seed < 3 else 0


@dataclass
class MountainDjinnStats(MonsterStats):
    char: str = "D"
    health: int = 18
    strength: list[int] = field(default_factory=lambda: [10,18])
    moves: int = 5
    dodging_ability: int = 5
    experience_when_killed: int = 30

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return 0.002 * seed if 4 < seed < 8 else 0


# SPECIAL MONSTERS


@dataclass
class PixieStats(MonsterStats):
    char: str = "P"
    health: int = 2
    strength: list[int] = field(default_factory=lambda: [1,1])
    moves: int = 5
    random_motility: int = 10
    dodging_ability: int = 7
    experience_when_killed: int = 3

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        return randint(0, 1) * 0.05
