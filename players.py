from __future__ import annotations
from player_classes import Player
import game_stats as stats

class Sawyer(Player):
    """Slow digger (takes half of initial moves each dig)
    Can pick gems
    LOW strength
    LOW health
    HIGH movement"""

    @property
    def is_hidden(self):
        return self.ability_active

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "%"
        self.name: str = "Sawyer"
        self.species: str = "sawyer"
        self.ignores: list[str] = self.ignores + ["dynamite"]

        self.stats = stats.SawyerStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str, int] | None = {"powder": 2}
        self.ability_display: str = "Hide"

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        """
        Determines if a Character is able to dig a certain kind of wall
        :param token_species: Token.species of the wall Token
        :return: True if can dig, False otherwise
        """
        if token_species == "rock":
            return self.shovels > 0 and self.remaining_moves >= self.stats.digging_moves
        if token_species in ["granite", "quartz"]:
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        """
        Checks if Sawyer can fight a certain monster
        :param token_species: MonsterToken.species to fight
        :return: True if the Sawyer can fight, False otherwise
        """
        return self.weapons > 0

    def on_player_level(self, instance, value):
        """Sawyer is a young, inexperienced but cunning character. Is it not particularly strong
        but her dexterity allows her to survive the most compromised situations.

        Sawyer increases 1 movement every 2 levels,
        1 health per level,
        1 recovery_end_of_level per level,
        1 max damage every 2 levels
        +0.05 in trap spotting chance every 3 levels
        """
        self._level_up_health(2)
        self.stats.recovery_end_of_level += 1

        if not value % 2 == 0:
            self._level_up_moves(1)
            self._level_up_strength((0, 1))

        if value % 3 == 0:
            self.stats.trap_spotting_chance += 0.05 \
                if self.stats.trap_spotting_chance < 1.0 else self.stats.trap_spotting_chance

        self._update_level_track(value)

    def perform_passive_action(self) -> None:
        """
        Placeholder, for the moment all passive actions are the same (finding traps) and defined within the superclass
        :return: None
        """
        super().perform_passive_action()

    def hide(self) -> None:
        """
        Hides Sawyer
        :return: None
        """
        self.special_items["powder"] -= 1
        self.ignores += ["pickable", "treasure"]
        self.token.color.a = 0.6  # changes transparency
        self.ability_active = True
        self.remaining_moves -= 1

    def unhide(self) -> None:
        """
        Reverts hiding
        :return: None
        """
        self.token.color.a = 1  # changes transparency
        self.ignores.remove("pickable")
        self.ignores.remove("treasure")
        self.ability_active = False

    def enhance_damage(self, damage: int) -> int:
        """
        Enhances attack damage
        :param damage: damage to enhance
        :return: enhanced damage
        """
        if self.ability_active:
            damage *= self.stats.advantage_strength_incr
        return damage

class CrusherJane(Player):
    """
    Can fight with no weapons (MEDIUM strength)
    Stronger if fight with weapons  (HIGH strength)
    Cannot pick gems
    LOW movement
    """

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "&"
        self.name: str = "Crusher Jane"
        self.species: str = "crusherjane"
        self.ignores: list[str] = self.ignores + ["powder", "dynamite", "treasure"]

        self.stats = stats.CrusherJaneStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] = {"weapons": None}
        self.ability_display: str = "Weapons"

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    @staticmethod
    def on_weapons(player: Player, value: int):
        """
        Notifies updates special item dictionary and calls super to update game button
        :param player: instance of the Player
        :param value: new weapon value
        :return: None
        """
        player.special_items["weapons"] = value
        super().on_weapons(player, value)

    def can_dig(self, token_species: str) -> bool:
        """
        Checks if CrusherJane can dig
        :param token_species: WallToken species to dig
        :return: True if can dig, False otherwise
        """
        if token_species == "rock":
            return self.shovels > 0 and self.remaining_moves >= self.stats.digging_moves
        if token_species in ["granite", "quartz"]:
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        """
        Crusher Jane can always fight
        :param token_species: MonsterToken.species to fight
        :return: True, always
        """
        return True

    def on_player_level(self, instance, value):
        """Crusher Jane is a big, strong and not particularly intelligent woman. Relies on brute strength and on her
        physical endurance to resist the most brutal hits.
        Crusher Jane increases 1 movement every 4 levels,
        2 health every level,
        (+1, +2) strength per level,
        1 recovery_end_of_level per level
        """
        self._level_up_health(3)
        self._level_up_strength((1, 2))
        if not value % 2 == 0:
            self.stats.recovery_end_of_level += 1
        if value % 4 == 0:
            self._level_up_moves(1)
        self._update_level_track(value)

    def perform_passive_action(self) -> None:
        """
        Placeholder, for the moment all passive actions are the same (finding traps) and defined within the superclass
        :return: None
        """
        super().perform_passive_action()

    def enhance_damage(self, damage: int) -> int:
        """
        Enhances attack damage
        :param damage: damage to enhance
        :return: enhanced damage
        """
        if self.ability_active:
            damage *= self.stats.advantage_strength_incr
        return damage

    def subtract_weapon(self) -> None:
        """
        Manages what happens with the ability button when the weapon is substracted
        :return: None
        """
        if self.ability_active:
            super().subtract_weapon()
            if self.weapons == 0:
                self.ability_active = False

class Hawkins(Player):
    """Can dig without shovels
    Does not pick shovels
    Can fight with weapons
    Cannot pick gems
    LOW health
    MEDIUM strength
    MEDIUM movement"""

    def __init__(self, attributes_dict: dict | None = None):
        super().__init__()
        self.char: str = "?"
        self.name: str = "Hawkins"
        self.species: str = "hawkins"
        self.ignores: list[str] = self.ignores+ ["powder", "treasure"]

        self.stats = stats.HawkinsStats()
        self._update_level_track(self.player_level)

        self.special_items: dict[str:int] | None = {"dynamite": 2}
        self.ability_display: str = "Dynamite"

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

    def can_dig(self, token_species: str) -> bool:
        """
        Checks if Hawkins can dig
        :param token_species: wall to dig
        :return: True if can dig, False otherwise
        """
        if token_species == "rock":
            return True
        if token_species == "granite":
            return self.shovels > 0 and self.remaining_moves >= self.stats.digging_moves
        if token_species == "quartz":
            return False
        raise ValueError(f"Invalid token_species {token_species}")

    def can_fight(self, token_species: str) -> bool:
        """
        Checks if Hawkins can fight
        :param token_species: MonsterToken.species to fight
        :return: True if Hawkins can fight, False otherwise
        """
        return self.weapons > 0

    def on_player_level(self, instance, value):
        """Hawkins is an old and wise man. It is trained by the most difficult situations of life, and it is strong
        for his age. But his most valuable asset is his wits.
        Hawkins increases 1 movement every 3 levels
        1 health point every level
        1 recovery_end_of_level every 3 levels
        1 max damage every level and 1 min damage every 2 levels
        + 0.05 in trap_spotting every 2 levels
        """
        self._level_up_health(2)
        self._level_up_strength((0, 1))
        if not value % 2 == 0:
            self._level_up_strength((1, 0))
        if value % 3 == 0:
            self._level_up_moves(1)
            self.stats.recovery_end_of_level += 1
        if value % 2 == 0:
            self.stats.trap_spotting_chance += 0.05 \
                if self.stats.trap_spotting_chance < 1.0 else self.stats.trap_spotting_chance
        self._update_level_track(value)

    def perform_passive_action(self) -> None:
        """
        Placeholder, for the moment all passive actions are the same (finding traps) and defined within the superclass
        :return: None
        """
        super().perform_passive_action()

    @property
    def using_dynamite(self):
        """
        Checks if Hawkins is using dynamite
        :return: True if using, False otherwise
        """
        return self.ability_active

    def throw_dynamite(self, tile: Tile) -> None:
        """
        Throws dynamite
        :param tile: Tile where dynamite lands
        :return: None
        """
        self.special_items["dynamite"] -= 1
        self.ability_active = False
        tile.dynamite_fall()
        self.remaining_moves -= 1

    def enhance_damage(self, damage: int) -> int:
        """
        Placeholder. Hawkins cannot enhance damage
        :param damage: damage to enhance
        :return: same damage
        """
        return damage
