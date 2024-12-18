from dataclasses import dataclass, field
from abc import ABC
from random import randint, uniform


class DungeonStats:

    mandatory_items: tuple[str,str,str,str,str] = ("%", "?", "&", " ", "o")

    def __init__(self, dungeon_level: int):
        self.stats_level = dungeon_level

    def size(self) -> int:
        return 8
        #return 6 + int(self.stats_level * 0.2)

    def gem_number(self) -> int:

        gem_number = int(self.stats_level * 0.15)
        gem_number = 1 if gem_number < 1 else gem_number
        return gem_number

    @property
    def torch_number(self) -> int:
        return 10

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
            RattleSnakeStats.char: RattleSnakeStats.calculate_frequency(self.stats_level),
            ClawJawStats.char: ClawJawStats.calculate_frequency(self.stats_level)
        }

        total_monster_frequency = sum(monster_frequencies.values())

        rock_wall_frequency = RockWallStats.calculate_frequency(self.stats_level)
        granite_wall_frequency = GraniteWallStats.calculate_frequency(self.stats_level)
        diggable_wall_frequency = rock_wall_frequency + granite_wall_frequency

        item_frequencies = {
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
        }

        all_frequencies = {**monster_frequencies, **item_frequencies}
        del monster_frequencies, item_frequencies
        return all_frequencies

@dataclass
class SceneryStats(ABC):
    char: str | None = None

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:
        pass


class RockWallStats(SceneryStats): # BALANCED
    char: str = "#"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        # RockWalls are common at early levels. Later they may be rare or (50% chance) or from rare to common
        if seed < randint (10, 15):
            return uniform(0.2, 0.7)
        if randint(1, 10) < 5:
            return uniform(0, 0.2)
        else:
            upper_limit = seed * 0.04 # max 0.72 at level 18
            return uniform(0.1, upper_limit) if seed < 18 else uniform(0.1, 0.7)


class GraniteWallStats(SceneryStats): # BALANCED
    char: str = "{"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        # GraniteWalls appear first at mid-levels. Later they may be rare or (50% chance) or from rare to common-ish
        if seed < randint (10, 15):
            return 0
        if randint(1, 10) < 5:
            return uniform(0, 0.2)
        else:
            upper_limit = seed * 0.03
            return uniform(0, upper_limit) if seed < 16 else uniform(0, 0.5)


class QuartzWallStats(SceneryStats): # BALANCED
    char: str = "*"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        # QuartzWalls appear first at late levels. Later they may be rare or (50% chance) or from rare to mid-frequent
        if seed < randint(20, 25):
            return 0
        if randint(1, 10) < 5:
            return uniform(0, 0.15)
        else:
            upper_limit = seed * 0.02
            return uniform(0, upper_limit) if seed < 18 else uniform(0, 0.4)


class ShovelStats(SceneryStats): # BALANCED
    char: str = "p"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is diggable wall frequency
        # Shovels depend on RockWalls + QuartzWalls frequency. They tend to lower frequencies
        upper_limit = seed * 0.1
        frequency =  uniform(0, upper_limit) - uniform(0,upper_limit)
        return frequency if frequency > 0 else 0


class WeaponStats(SceneryStats): # BALANCED
    char: str = "x"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is monster frequency
        # Weapons depend on pooled monster frequency. They tend to lower frequencies
        upper_limit = seed * 0.3
        frequency =  uniform(0, upper_limit) - uniform(0, upper_limit / 2)
        return frequency if frequency > 0 else 0


class PowderStats(SceneryStats): # BALANCED
    char: str = "h"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is level
        # Powder may not appear at very first levels. It tends to lower frequencies depending on level.
        if randint(1, 10) < 4 or seed < 3:
            return 0
        else:
            upper_limit = seed * 0.03 if seed < 15 else 0.5
            frequency = uniform(0, upper_limit) - uniform(0, upper_limit)
            return frequency if frequency > 0 else 0


class DynamiteStats(SceneryStats): # BALANCED
    char: str = "d"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is level
        # Dynamite may not appear at very first levels. It tends to lower frequencies depending on level.
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

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is monster frequency
        # Items depend on pooled monster frequency. They have 30% change to get a frequency.
        # They tend to lower frequencies.
        if randint(1,10) < 4:
            return 0
        frequency = uniform(0, seed / 5) - uniform(0, seed / 5)
        return frequency if 0 < frequency < 0.5 else 0


@dataclass
class JerkyStats(ItemStats):  # BALANCED
    char: str = "j"
    effect_size: float = 0.3  # percentage of increase respect character stats
    min_effect: int = 2


@dataclass
class CoffeeStats(ItemStats):  # BALANCED
    char: str = "c"
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 3


@dataclass
class TobaccoStats(ItemStats):  # BALANCED
    char: str = "l"
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 3


@dataclass
class WhiskyStats(ItemStats):  # BALANCED
    char: str = "w"
    effect_size: float = 0.3  # percentage of increase respect character stats
    effect_duration: int = 3


@dataclass
class TalismanStats(ItemStats): # BALANCED
    char: str = "t"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is level
        # Talisman is an exception among items. It may not appear at very first levels and has only 50% chance to get
        # a frequency. Frequency is always low.
        if randint(1, 10) < 5 or seed < 6:
            return 0
        else:
            frequency = uniform(0, seed * 0.3) - uniform(0, seed * 0.3)
            return frequency if 0 < frequency < 0.3 else 0


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
class SawyerStats(PlayerStats): # BALANCED
    health: int = 200 #5
    strength: list[int] = field(default_factory=lambda: [1,2])
    advantage_strength_incr: int = 2
    moves: int = 4
    digging_moves: int = 3


@dataclass
class HawkinsStats(PlayerStats):  # BALANCED
    health: int = 200 #7
    strength: list[int] = field(default_factory=lambda: [1,3])
    moves: int = 3
    shooting_range: int = 2


@dataclass
class CrusherJaneStats(PlayerStats):  # BALANCED
    weapons: int = 4
    health: int = 200#10
    strength: list[int] = field(default_factory=lambda: [2,4])
    advantage_strength_incr: int = 1
    moves: int = 3


@dataclass
class MonsterStats(CharacterStats, ABC):

    random_motility: float = 0  # from 0 to 1. Percentage of moves when random movement. If only movement, set to 1.0
    dodging_ability: int = 0  # from 0 to 14. 14 always dodges if at least 1 free tile nearby
                              # 10 always dodges if 4 free tiles nearby
    dodging_moves: int = 1
    max_attacks: int | None = None
    remaining_attacks: int | None = None

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        pass


# RANDOM MOVEMENT MONSTERS


@dataclass
class KoboldStats(MonsterStats): # BALANCED
    char: str = "K"
    health: int = 3
    strength: list[int] = field(default_factory=lambda: [1,3])
    moves: int = 5
    random_motility: float = 1.0
    dodging_ability: int = 7
    experience_when_killed: int = 5

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float: # seed is level
        # Kobolds decrease with level increase
        if seed < randint(4,7):
            return uniform(0.2, 0.5) / seed
        else:
            return 0


@dataclass
class BlindLizardStats(MonsterStats):  # BALANCED
    char: str = "L"
    health: int = 6
    strength: list[int] = field(default_factory=lambda: [4,8])
    moves: int = 4
    random_motility: float = 1.0
    dodging_ability: int = 3
    experience_when_killed: int = 15

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # BlindLizards decrease with level increase
        if seed < randint (6,8):
            return 0
        else:
            return uniform(0.2, 0.7) / (seed / 2)


@dataclass
class BlackDeathStats(MonsterStats):  # BALANCED
    char: str = "B"
    health: int = 1
    strength: list[int] = field(default_factory=lambda: [5,50])
    moves: int = 7
    random_motility: float = 1.0
    dodging_ability: int = 12
    experience_when_killed: int = 30

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Blackdeath can show up at any level except the first
        if seed == 1:
            return 0
        if randint(1, 10) == 10:
            return uniform(0.1, 0.2)
        else:
            return uniform(0, 0.05)


# DIRECT MOVEMENT MONSTERS


@dataclass
class CaveHoundStats(MonsterStats):  # BALANCED
    char: str = "H"
    health: int = 4
    strength: list[int] = field(default_factory=lambda: [2,5])
    moves: int = 6
    random_motility: float = 1.0
    dodging_ability: int = 9
    experience_when_killed: int = 10

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        # CaveHound may overlap with Kobold. They increase up to certain point then decrease steadily
        if seed < randint(4,6):
            return 0
        if seed < randint(6, 11):
            return uniform(0.1, 0.25) * seed / 3
        if seed < randint(12, 14):
            return uniform(0.6, 0.9) / (seed / 2)
        else:
            return 0


@dataclass
class GrowlStats(MonsterStats):  # BALANCED
    char: str = "G"
    health: int = 10
    strength: list[int] = field(default_factory=lambda: [7,12])
    moves: int = 5
    random_motility: float = 0.5
    dodging_ability: int = 5
    experience_when_killed: int = 22

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Growls appear and in increasing frequencies before slowly fading
        if seed < 14:
            return 0
        elif seed < 18:
            return uniform(0,0.2)
        elif seed < 24:
            return uniform (0.04, 0.1) * (seed / 5)
        elif seed < 28:
            return uniform(0,0.2)
        else:
            return 0


@dataclass
class RockGolemStats(MonsterStats):  # BALANCED
    char: str = "R"
    health: int = 75
    strength: list[int] = field(default_factory=lambda: [15,30])
    moves: int = 3
    dodging_ability: int = 0
    experience_when_killed: int = 60

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # RockGolems appear with same odds in a wide range of levels and afterward they may still appear
        if seed < randint(14, 17):
            return 0
        if seed < randint(23, 25):
            return uniform(0.1,0.4)
        else:
            return uniform(0, 0.15)


# SMART MOVEMENT MONSTERS


@dataclass
class DarkGnomeStats(MonsterStats):  # BALANCED
    char: str = "O"
    health: int = 3
    strength: list[int] = field(default_factory=lambda: [1,2])
    moves: int = 5
    random_motility: float = 0.5
    dodging_ability: int = 10
    experience_when_killed: int = 5

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # DarkGnome show up a bit later, increase up to certain point then decrease steadily
        if seed < randint(2,3):
            return 0
        if seed < 8:
            return uniform(0.1, 0.2) * (seed / 2)
        if seed < 11:
            return uniform(0.5, 0.8) / (seed / 2)
        else:
            return 0


@dataclass
class NightmareStats(MonsterStats): # BALANCED
    char: str = "N"
    health: int = 15
    strength: list[int] = field(default_factory=lambda: [10,15])
    random_motility: float = 0.2
    moves: int = 5 # 8
    dodging_ability: int = 10
    experience_when_killed: int = 25

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Nightmares own the mine. They appear with same frequency in a wide range of levels and afterward they may
        # still appear
        if seed < randint(12, 18):
            return 0
        if seed < randint(22, 25):
            return uniform(0.2, 0.4)
        else:
            return uniform(0.1, 0.25)


@dataclass
class LindWormStats(MonsterStats):  # BALANCED
    char: str = "Y"
    health: int = 130
    strength: list[int] = field(default_factory=lambda: [50,75])
    moves: int = 5
    dodging_ability: int = 4
    experience_when_killed: int = 100

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Lindworms are very rare at the beginning, but they increase frequency steadily as level increases
        if seed < 25:
            return 0
        else:
            frequency = 0.03 * seed / 5
            return frequency if frequency < 0.5 else 0.5


# GHOSTS


@dataclass
class WanderingShadowStats(MonsterStats):  # BALANCED
    char: str = "S"
    health: int = 4
    strength: list[int] = field(default_factory=lambda: [2,8])
    moves: int = 7
    random_motility: float = 1.0
    dodging_ability: int = 14
    experience_when_killed: int = 15

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # WanderingShadows appear with same odds in a wide range of levels before suddenly disappearing
        if seed < randint(6, 8):
            return 0
        if seed < randint(9, 20):
            return uniform(0.1,0.4)
        else:
            return 0


@dataclass
class DepthsWispStats(MonsterStats):  # BALANCED
    char: str = "W"
    health: int = 1
    strength: list[int] = field(default_factory=lambda: [1,1])
    moves: int = 4
    dodging_ability: int = 1.0
    experience_when_killed: int = 3

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Wisps increase with level increase up to certain point then decrease suddenly
        if seed == 1:
            return 0
        if seed < randint(4, 7):
            return uniform(0.05, 0.15) * (seed / 2)
        if seed < randint(8,10):
            return uniform(0, 0.15)
        else:
            return 0


@dataclass
class MountainDjinnStats(MonsterStats):  # BALANCED
    char: str = "D"
    health: int = 30
    strength: list[int] = field(default_factory=lambda: [20,25])
    moves: int = 7
    dodging_ability: int = 1.0
    experience_when_killed: int = 50

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        # MountainDjinns increase in chance when level increases up to a point. Later they appear with lower frequency
        if seed < randint(21,25):
            return 0
        if seed < 35:
            frequency = uniform(0,0.1) * seed / 4
            return frequency if frequency < 0.6 else 0.6
        else:
            return uniform(0.1, 0.4)


# SPECIAL MONSTERS


@dataclass
class PixieStats(MonsterStats):  # BALANCED
    char: str = "P"
    health: int = 2
    strength: list[int] = field(default_factory=lambda: [1,1])
    moves: int = 5
    random_motility: float = 1.0
    dodging_ability: int = 14
    experience_when_killed: int = 5

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Pixie can show up at any level
        if randint(1,10) == 10:
            return uniform(0.2, 0.4)
        else:
            return uniform(0,0.1)

@dataclass
class RattleSnakeStats(MonsterStats):
    char: str = "V"
    health: int = 5
    strength: list[int] = field(default_factory=lambda: [2,10])
    moves: int = 10
    max_attacks: int = 1
    random_motility: float = 0.2
    dodging_ability: int = 5
    experience_when_killed: int = 15

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # RattleSnake can show up at any level in a range of levels
        if seed < 2 or seed >= 15:
            return 0
        elif seed < 10:
            return uniform(0.0, 0.4)
        elif seed < 15:
            return uniform(0,0.2)


@dataclass
class ClawJawStats(MonsterStats):
    char: str = "C"
    health: int = 5
    strength: list[int] = field(default_factory=lambda: [10,30])
    moves: int = 10
    random_motility: float = 0.7
    dodging_ability: int = 7
    experience_when_killed: int = 30

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # ClawJaw can show up at any level from a certain level
        if seed < 2:
            return 0
        elif seed < 10:
            return uniform(0.0, 0.2)
        elif seed >= 10:
            return uniform(0,0.4)
