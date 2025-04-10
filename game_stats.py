from __future__ import annotations

from dataclasses import dataclass, field
from abc import ABC
from random import randint, uniform
from typing import ClassVar


class DungeonStats:
    """
    The game progression is designed to last 30 levels. From level 30, levels will be still created but no
    progression will be happening
    """
    def __init__(self, dungeon_level: int):
        self.stats_level = dungeon_level
        self.max_total_freq: float = 0.8  # max total frequency of all items placed

    @property
    def size(self) -> int:
        return 6 + int(self.stats_level * 0.2)

    @property
    def gem_number(self) -> int:

        gem_number = int(self.stats_level * 0.1)
        gem_number = 1 if gem_number < 1 else gem_number
        return gem_number

    @property
    def talisman_number(self) -> int:
        # Talisman does not appear in very first levels. In other levels has low frequency, ges higher when characters
        # are dead
        from player_classes import Player

        dead_char: int = len(Player.dead_data)
        trigger: int = randint(1, 10)

        if dead_char == 0:
            if trigger < 7 or self.stats_level < 4:
                return 0
            return 1
        else:
            if trigger < 3:
                return 0
            if trigger < 9:
                return 1
            return 2

    @property
    def dynamite_number(self) -> int:
        # dynamites are rare unless Hawkins has run out of dynamites
        if self.stats_level < 3:
            return 0

        from player_classes import Player

        for player in Player.exited:
            if player.species == "hawkins":
                dynamites: int = player.special_items["dynamite"]
                trigger = randint(1, 10)

                if dynamites == 0:
                    if trigger < 4:
                        return 0
                    if trigger < 9:
                        return 1
                    else:
                        return 2
                else:
                    if trigger == 10 and dynamites < 5:  # jackpot
                        return 2
                    if trigger < 4 or trigger < dynamites * 2 or dynamites > 6:
                        return 0
                    else:
                        return 1

        # if hawkins not it players exited (dead)
        return 0

    @property
    def powder_number(self) -> int:
        # powder are rare unless Sawyer has run out of powders
        if self.stats_level < 3:
            return 0

        from player_classes import Player

        for player in Player.exited:
            if player.species == "sawyer":
                powders: int = player.special_items["powder"]
                trigger = randint(1, 10)

                if powders == 0:
                    if trigger < 4:
                        return 0
                    if trigger < 9:
                        return 1
                    else:
                        return 2
                else:
                    if trigger == 10 and powders < 6:  # jackpot
                        return 2
                    if trigger < 4 or trigger < powders * 2 or powders > 8:
                        return 0
                    else:
                        return 1

    @property
    def torch_number(self) -> int:
        torches = randint(1,self.size)
        return torches if torches < 5 else 5

    def level_progression(self) -> dict[str:float]:
        """
        Organizes in a dictionary the frequency of items in the level
        :return: dictionary with item.char as key and item frequency as value
        """
        total_freq: float | None = None
        while total_freq is None or total_freq > self.max_total_freq:

            total_monster_freq: float | None = None
            while (total_monster_freq is None or
                   not MonsterStats.min_group_freq <= total_monster_freq <= MonsterStats.max_group_freq):
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
                    PenumbraStats.char: PenumbraStats.calculate_frequency(self.stats_level),
                    ClawJawStats.char: ClawJawStats.calculate_frequency(self.stats_level),
                }
                total_monster_freq = sum(monster_frequencies.values())

            total_wall_freq: float | None = None
            while (total_wall_freq is None or
                   not WallStats.min_group_freq <= total_wall_freq <= WallStats.max_group_freq):
                wall_frequencies = {
                    RockWallStats.char: RockWallStats.calculate_frequency(self.stats_level),
                    GraniteWallStats.char: GraniteWallStats.calculate_frequency(self.stats_level),
                    QuartzWallStats.char: QuartzWallStats.calculate_frequency(self.stats_level)
                }
                total_wall_freq = sum(wall_frequencies.values())

            total_weapon_shovel_freq: float | None = None
            while (total_weapon_shovel_freq is None or
                   not WeaponShovelStats.min_group_freq <= total_weapon_shovel_freq <= WeaponShovelStats.max_group_freq):
                diggable_wall_frequency = wall_frequencies[RockWallStats.char] + wall_frequencies[GraniteWallStats.char]
                weapon_shovel_frequencies = {
                    ShovelStats.char: ShovelStats.calculate_frequency(diggable_wall_frequency),
                    WeaponStats.char: WeaponStats.calculate_frequency(total_monster_freq)
                }
                total_weapon_shovel_freq = sum(weapon_shovel_frequencies.values())

            total_item_freq: float | None = None
            while (total_item_freq is None or
                   not ItemStats.min_group_freq <= total_item_freq <= ItemStats.max_group_freq):
                item_frequencies = {
                    JerkyStats.char: JerkyStats.calculate_frequency(total_monster_freq),
                    CoffeeStats.char: CoffeeStats.calculate_frequency(total_monster_freq),
                    WhiskyStats.char: WhiskyStats.calculate_frequency(total_monster_freq),
                    TobaccoStats.char: TobaccoStats.calculate_frequency(total_monster_freq),
                }
                total_item_freq = sum(item_frequencies.values())

            total_trap_freq: float | None = None
            while (total_trap_freq is None or
                   not TrapStats.min_group_freq <= total_trap_freq <= TrapStats.max_group_freq):
                trap_frequency = {
                    TrapStats.char: TrapStats.calculate_frequency(self.stats_level)
                }
                total_trap_freq = sum(trap_frequency.values())

            total_freq: float = (total_monster_freq +
                                 total_wall_freq +
                                 total_weapon_shovel_freq +
                                 total_item_freq +
                                 total_trap_freq)

        all_frequencies = {**monster_frequencies,
                           **wall_frequencies,
                           **weapon_shovel_frequencies,
                           **item_frequencies,
                           **trap_frequency}

        del monster_frequencies, wall_frequencies, weapon_shovel_frequencies, item_frequencies, trap_frequency
        return all_frequencies

@dataclass
class WallStats(ABC):
    char: str | None = None

    min_group_freq: ClassVar[float] = 0.15
    max_group_freq: ClassVar[float] = 0.5

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:
        pass


@dataclass
class WeaponShovelStats(ABC):
    char: str | None = None

    min_group_freq: ClassVar[float] = 0.05
    max_group_freq: ClassVar[float] = 0.25

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:
        pass


@dataclass
class ItemStats(ABC):
    char: str | None = None
    effect_size: float | None = None
    effect_duration: int | None = None
    use_time: int = 1

    min_effect: int = 3
    max_effect: int | None = None

    min_group_freq: ClassVar[float] = 0.0
    max_group_freq: ClassVar[float] = 0.18

    @staticmethod
    def calculate_frequency(seed: int | float) -> float: # seed is monster frequency
        # Items depend on pooled monster frequency. They have 40% change to get a frequency.
        if randint(1,10) < 4:
            return 0
        if randint(1, 10) < 8:
            frequency = uniform(0, seed * 0.2)
            return frequency if frequency < 0.075 else 0.075
        else:
            return 0.05


class RockWallStats(WallStats): # BALANCED
    char: str = "#"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        # RockWalls are common at early levels. Later they may be rare or (50% chance) or from rare to common
        if seed < 10:
            return  uniform(0.15, 0.5)
        if randint(1, 10) < 5:
            return uniform(0, 0.3)
        else:
            return uniform(0, 0.2)


class GraniteWallStats(WallStats): # BALANCED
    char: str = "{"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        # GraniteWalls appear first at level 10. Later they may be rare or (50% chance) or from rare to common-ish
        if seed < 10:
            return 0
        if randint(1, 10) < 5:
            return uniform(0, 0.2)
        else:
            return uniform(0.05,0.35)


class QuartzWallStats(WallStats): # BALANCED
    char: str = "*"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is level
        # QuartzWalls appear first at level 22. Later they may be rare or (50% chance) or from rare to mid-frequent
        if seed < 22:
            return 0
        if randint(1, 10) < 7:
            return uniform(0, 0.15)
        else:
            return uniform(0.05, 0.25)


class ShovelStats(WeaponShovelStats): # BALANCED
    char: str = "p"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is diggable wall frequency
        if randint(1, 10) < 7:
            # Shovels depend on RockWalls + QuartzWalls frequency.
            upper_limit = seed * 0.35
        else:
            upper_limit = 0.12
        frequency =  uniform(0, upper_limit)
        return frequency if frequency < 0.12 else 0.12


class WeaponStats(WeaponShovelStats): # BALANCED
    char: str = "x"

    @staticmethod
    def calculate_frequency(seed: int | float) -> float:  # seed is monster frequency
        if randint(1, 10) < 7:
            # Weapons depend on pooled monster frequency.
            upper_limit = seed * 0.7
        else:
            upper_limit = 0.15
        frequency =  uniform(0, upper_limit)
        return frequency if frequency < 0.15 else 0.15


class PowderStats: # BALANCED
    char: str = "h"

    @staticmethod
    def calculate_frequency() -> None:
        """
        Powders are not handled by frequencies. See @property DungeonStats.powder_number
        :return: None
        """
        pass


class DynamiteStats: # BALANCED
    char: str = "d"

    @staticmethod
    def calculate_frequency() -> None:
        """
        Dynamites are not handled by frequencies. See @property DungeonStats.dynamite_number
        :return: None
        """
        pass


@dataclass
class JerkyStats(ItemStats):  # BALANCED
    char: str = "j"
    effect_size: float = 0.3  # percentage of increase respect character stats


@dataclass
class CoffeeStats(ItemStats):  # BALANCED
    char: str = "c"
    effect_size: float = 0.4  # percentage of increase respect character stats
    effect_duration: int = 7


@dataclass
class TobaccoStats(ItemStats):  # BALANCED
    char: str = "l"
    effect_size: float = 0.4  # percentage of increase respect character stats
    effect_duration: int = 7


@dataclass
class WhiskyStats(ItemStats):  # BALANCED
    char: str = "w"
    effect_size: float = 0.4  # percentage of increase respect character stats
    effect_duration: int = 7


@dataclass
class TalismanStats: # BALANCED
    char: str = "t"
    use_time: int = 1

    @staticmethod
    def calculate_frequency() -> None: # seed is level
        """
        Talismans are not handled by frequencies. See @property DungeonStats.talisman_number
        :return:
        """
        pass


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

    shovels: int = 3
    digging_moves: int = 1
    weapons: int = 3
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
    health: int = 5
    strength: list[int] = field(default_factory=lambda: [1,3])
    advantage_strength_incr: int = 4
    moves: int = 4
    digging_moves: int = 3
    trap_spotting_chance: float = 0.2
    trap_disarming_chance: float = 0.3


@dataclass
class HawkinsStats(PlayerStats):  # BALANCED
    health: int = 8
    strength: list[int] = field(default_factory=lambda: [1,4])
    moves: int = 3
    shooting_range: int = 2
    trap_spotting_chance: float = 0.3
    trap_disarming_chance: float = 0.7


@dataclass
class CrusherJaneStats(PlayerStats):  # BALANCED
    weapons: int = 4
    health: int = 10
    strength: list[int] = field(default_factory=lambda: [2,5])
    advantage_strength_incr: int = 2
    moves: int = 3
    trap_spotting_chance: float = 0.1
    trap_disarming_chance: float = 0.0


@dataclass
class MonsterStats(CharacterStats, ABC):

    random_motility: float = 0  # from 0 to 1. Percentage of moves when random movement. If only movement, set to 1.0
    dodging_ability: int = 0  # from 0 to 14. 14 always dodges if at least 1 free tile nearby
                              # 10 always dodges if 4 free tiles nearby
    dodging_moves: int = 1
    max_attacks: int | None = None
    remaining_attacks: int | None = None

    min_group_freq: ClassVar[float] = 0.075
    max_group_freq: ClassVar[float] = 0.3

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        pass


# RANDOM MOVEMENT MONSTERS


@dataclass
class KoboldStats(MonsterStats): # BALANCED
    char: str = "K"
    health: int = 3
    strength: list[int] = field(default_factory=lambda: [1,2])
    moves: int = 5
    random_motility: float = 1.0
    dodging_ability: int = 7
    experience_when_killed: int = 6

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float: # seed is level
        # Kobolds decrease with level increase
        if seed < 3:
            return uniform (0.05, 0.2)
        elif seed < 8:
            return uniform(0, 0.075)
        else:
            return 0


@dataclass
class BlindLizardStats(MonsterStats):  # BALANCED
    char: str = "L"
    health: int = 6
    strength: list[int] = field(default_factory=lambda: [2,6])
    moves: int = 4
    random_motility: float = 1.0
    dodging_ability: int = 3
    experience_when_killed: int = 18

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        if seed < 6 or seed >= 15:
            return 0
        else:
            return uniform(0, 0.1)


@dataclass
class BlackDeathStats(MonsterStats):  # BALANCED
    char: str = "B"
    health: int = 1
    strength: list[int] = field(default_factory=lambda: [3,50])
    moves: int = 7
    random_motility: float = 1.0
    dodging_ability: int = 12
    experience_when_killed: int = 22

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Blackdeath can show up at any level except the first
        if seed == 1:
            return 0
        if randint(1, 10) == 10:
            return uniform(0.05, 0.1)
        else:
            return uniform(0, 0.05)


# DIRECT MOVEMENT MONSTERS


@dataclass
class CaveHoundStats(MonsterStats):  # BALANCED
    char: str = "H"
    health: int = 4
    strength: list[int] = field(default_factory=lambda: [2,4])
    moves: int = 6
    random_motility: float = 1.0
    dodging_ability: int = 9
    experience_when_killed: int = 12

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        # CaveHound may overlap with Kobold. They increase up to certain point then decrease steadily
        if seed < 4:
            return 0
        if seed < 11:
            return uniform(0, 0.05)
        if seed < 14:
            return uniform(0.05, 0.15)
        else:
            return 0


@dataclass
class GrowlStats(MonsterStats):  # BALANCED
    char: str = "G"
    health: int = 60
    strength: list[int] = field(default_factory=lambda: [4,8])
    moves: int = 6
    random_motility: float = 0.5
    dodging_ability: int = 5
    experience_when_killed: int = 30

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Growls appear and in increasing frequencies before slowly fading
        if seed < 14:
            return 0
        elif seed < 18:
            return uniform(0,0.075)
        elif seed < 24:
            return uniform (0.025, 0.05)
        elif seed < 28:
            return uniform(0,0.05)
        else:
            return 0


@dataclass
class RockGolemStats(MonsterStats):  # BALANCED
    char: str = "R"
    health: int = 140
    strength: list[int] = field(default_factory=lambda: [12,20])
    moves: int = 3
    dodging_ability: int = 0
    experience_when_killed: int = 75

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # RockGolems appear with same odds in a wide range of levels and afterward they may still appear
        if seed < 16:
            return 0
        if seed < 25:
            return uniform(0,0.1)
        else:
            return uniform(0, 0.05)


# SMART MOVEMENT MONSTERS


@dataclass
class DarkGnomeStats(MonsterStats):  # BALANCED
    char: str = "O"
    health: int = 3
    strength: list[int] = field(default_factory=lambda: [1,3])
    moves: int = 5
    random_motility: float = 0.5
    dodging_ability: int = 10
    experience_when_killed: int = 6

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # DarkGnome show up a bit later, increase up to certain point then decrease steadily
        if seed < 3:
            return 0
        if seed < 8:
            return uniform(0, 0.05)
        if seed < 11:
            return uniform(0.05, 0.1)
        else:
            return 0


@dataclass
class NightmareStats(MonsterStats): # BALANCED
    char: str = "N"
    health: int = 15
    strength: list[int] = field(default_factory=lambda: [2,5])
    random_motility: float = 0.2
    moves: int = 9
    dodging_ability: int = 10
    experience_when_killed: int = 30

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Nightmares own the mine. They appear with same frequency in a wide range of levels and afterward they may
        # still appear
        if seed < 15:
            return 0
        if seed < 23:
            return uniform(0.025, 0.1)
        else:
            return uniform(0, 0.05)


@dataclass
class LindWormStats(MonsterStats):  # BALANCED
    char: str = "Y"
    health: int = 230
    strength: list[int] = field(default_factory=lambda: [20,30])
    moves: int = 7
    dodging_ability: int = 4
    experience_when_killed: int = 150

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Lindworms are very rare at the beginning, but they increase frequency steadily as level increases
        if seed < 22:
            return 0
        elif seed < 25:
            return uniform(0, 0.025)
        elif seed < 30:
            return uniform(0, 0.05)
        else:
            return uniform(0.05, 0.1)


# GHOSTS


@dataclass
class WanderingShadowStats(MonsterStats):  # BALANCED
    char: str = "S"
    health: int = 4
    strength: list[int] = field(default_factory=lambda: [1,4])
    moves: int = 7
    random_motility: float = 1.0
    dodging_ability: int = 14
    experience_when_killed: int = 22

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # WanderingShadows appear with same odds in a wide range of levels before suddenly disappearing
        if seed < 6:
            return 0
        if seed < 20:
            return uniform(0.025,0.075)
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
        if seed < 7:
            return uniform(0, 0.05)
        if seed < 10:
            return uniform(0, 0.1)
        else:
            return 0


@dataclass
class MountainDjinnStats(MonsterStats):  # BALANCED
    char: str = "D"
    health: int = 65
    strength: list[int] = field(default_factory=lambda: [7,12])
    moves: int = 7
    dodging_ability: int = 1.0
    experience_when_killed: int = 40

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:
        # MountainDjinns increase in chance when level increases up to a point. Later they appear with lower frequency
        if seed < 21:
            return 0
        if seed < 30:
            return uniform(0,0.075)
        else:
            return uniform(0.05, 0.1)


# SPECIAL MONSTERS


@dataclass
class PixieStats(MonsterStats):  # BALANCED
    char: str = "P"
    health: int = 2
    strength: list[int] = field(default_factory=lambda: [1,1])
    moves: int = 4
    random_motility: float = 1.0
    dodging_ability: int = 14
    experience_when_killed: int = 6

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Pixie can show up at any level
        if randint(1,10) > 8:
            return uniform(0.025, 0.1)
        else:
            return uniform(0,0.05)

@dataclass
class RattleSnakeStats(MonsterStats):
    char: str = "V"
    health: int = 5
    strength: list[int] = field(default_factory=lambda: [2,10])
    moves: int = 8
    max_attacks: int = 1
    random_motility: float = 0.2
    dodging_ability: int = 5
    experience_when_killed: int = 27

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # RattleSnake can show up at any level in a range of levels
        if seed < 5 or seed >= 20:
            return 0
        elif seed < 10:
            return uniform(0.0, 0.025)
        else:
            return uniform(0,0.1)


@dataclass
class PenumbraStats(MonsterStats):
    char: str = "A"
    health: int = 8
    strength: list[int] = field(default_factory=lambda: [3,7])
    moves: int = 12 # do not go below 7 or will not move due to max_attack and retreat moves
    max_attacks: int = 3
    random_motility: float = 0.4
    dodging_ability: int = 13
    experience_when_killed: int = 42

    # exclusive of penumbra. Minimum distance of retreat from player
    min_retreat_dist = 1  #3

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # Penumbra can show up at any starting at level 15
        if seed < 15:
            return 0
        elif seed < 20:
            return uniform(0.0, 0.075)
        else:
            return uniform(0,0.1)


@dataclass
class ClawJawStats(MonsterStats):
    char: str = "C"
    health: int = 22
    strength: list[int] = field(default_factory=lambda: [2,5])
    moves: int = 7
    random_motility: float = 0.7
    dodging_ability: int = 5
    experience_when_killed: int = 32

    def __post_init__(self):
        if self.max_attacks is None:
            self.max_attacks = self.moves

    @staticmethod
    def calculate_frequency(seed: int) -> float:  # seed is level
        # ClawJaw can show up at any level from a certain level
        if seed < 10:
            return 0
        elif seed < 15:
            return uniform(0, 0.05)
        else:
            return uniform(0, 0.08)

@dataclass
class TrapStats:
    char: str = "!"
    base_damage: list[int] = field(default_factory=lambda: [2, 4])
    base_experience_when_disarmed: int = 8
    experience_when_found: int = 10

    min_group_freq: ClassVar[float] = 0.0
    max_group_freq: ClassVar[float] = 0.12

    @staticmethod
    def calculate_frequency(seed: int) -> float: # seed is level
        # Traps start showing late and increase frequency with increasing level
        if seed < 5:
            return 0
        trigger = randint(1,10)
        if seed < 10 and trigger > 5:
            return uniform(0, 0.05)
        if seed < 15 and trigger > 4:
            return uniform(0, 0.08)
        if seed < 20 and trigger > 3:
            return uniform(0, 0.10)
        if seed >= 20 and trigger > 2:
            return uniform(0, 0.12)
        return 0

    def calculate_damage(self, dungeon_level: int) -> int:
        """
        Damage dealt by traps increases with dungeon level
        :param dungeon_level: current level of the dungeon
        :return: damage dealt by the trap
        """
        level: int = dungeon_level // 4
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
