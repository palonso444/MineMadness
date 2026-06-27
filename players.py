from __future__ import annotations
from player_class import Player
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

        self.special_items: dict[str, int] = {"powder": 2}
        self.ability_display: str = "Hide"

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

        self.initialize_upgrade_track()

    def get_upgrade_cost(self) -> None:
        pass

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

        self.special_items: dict[str:int] = {"weapons": None}
        self.ability_display: str = "Weapons"

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

        self.initialize_upgrade_track()

    def get_upgrade_cost(self) -> None:
        pass

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

        self.special_items: dict[str:int] = {"dynamite": 2}
        self.ability_display: str = "Dynamite"

        if attributes_dict is not None:
            self.overwrite_attributes(attributes_dict)

        self.initialize_upgrade_track()

    def get_upgrade_cost(self) -> None:
        pass

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
