from __future__ import annotations

from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.app import App

from monster_classes import Monster
from tokens_solid import SceneryToken, PlayerToken, MonsterToken
from tokens_fading import ExplosionToken


class Tile(Button):
    """
    Class defining each one of the Tiles of the DungeonLayout grid
    """
    def __init__(self, row: int, col:int, kind: str, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(**kwargs)

        self.row: int = row
        self.col: int = col
        self.position: tuple[int,int] = row, col
        self.kind: str = kind
        self.tokens: dict [str:list[Token]] = {
            "player": [],
            "monster": [],
            "trap": [],
            "wall": [],
            "pickable": [],
            "treasure": [],
            "light": []
        }
        self.dungeon: DungeonLayout = dungeon_instance

        self.first_click_time: float | None = None
        self.double_click_interval: float = 0.5  # max time in seconds between double clicks

    @staticmethod
    def update_tokens_pos(tile, tile_pos) -> None:
        """
        This callback updates the position of the Tokens when the pos of the Tile changes. Removed its position from
        DungeonLayout.level_start list. When len(level_start) == 0, level starts
        :param tile: Tile that changes the pos
        :param tile_pos: new pos value of the Tile
        :return: None
        """
        for token_list in tile.tokens.values():
            for token in token_list:
                token.pos = tile.pos[0] + token.pos_modifier[0], tile.pos[1] - token.pos_modifier[1]  # (x,y)
                tile.dungeon.positions_to_update -= 1

    def set_token(self, token:Token) -> None:
        """
        Sets the specified Token as part of Tile.tokens dictionary
        :param token: Token to set
        :return: None
        """
        self.tokens[token.kind].append(token)

    def get_token(self, token_kind: str) -> Token:
        """
        Returns from Tile.tokens the Token of the specified kind
        :param token_kind: Token.kind of the Token
        :return: Token of the specified kind
        """
        return next((token for token in self.tokens[token_kind]))

    def remove_token(self, token:Token) -> None:
        """
        Removes from Tile.tokens dictionary the specified Token
        :param token: Token to remove
        :return: None
        """
        self.tokens[token.kind].remove(token)

    def delete_all_tokens(self) -> None:
        """
        Clears the Tile of all its Tokens
        :return: None
        """
        for token_list in self.tokens.values():
            #while len(token_list) > 0:
                #token_list[0].delete_token(self)
            for token in token_list:
                token.delete_token(self)

    @property
    def has_character(self) -> bool:
        """
        Checks if the Tile has a Token with associated character of any kind: Monster, Player, Trap, etc.
        :return: True if Tile has a character, False otherwise
        """
        return any(token.character is not None
                   for token_list in self.tokens.values()
                   for token in token_list
                   )

    @property
    def has_all_characters_hidden(self) -> bool:
        """
        Checks if all Token.characters of the Tile are hidden
        :return: True if all Token.characters are hidden, False otherwise
        """
        if not self.has_character:
            raise Exception(f"Tile {self.position} has no characters!")

        return not any(
            token.character is not None and not token.character.is_hidden
            for token_list in self.tokens.values()
            for token in token_list
        )

    def has_token(self, token_kind: str | None = None, token_species: str | None = None) -> bool:
        """
        Checks if the Tile has a Token of the specified Token.kind and Token.species (optional)
        :param token_kind: Token.kind to check
        :param token_species: Token.species to check (optional)
        :return: True if the Tile has a Token of the specified kind and species, False otherwise
        """
        if token_kind is None:
            if token_species is not None:
                raise ValueError("token_kind cannot be None if token_species not None")
            return any(len(token_list) > 0 for token_list in self.tokens.values())

        return (len (self.tokens[token_kind]) > 0 and
                (token_species is None or any(token.species == token_species for token in self.tokens[token_kind])))

    def is_nearby(self, position: tuple[int,int]) -> bool:
        """
        Checks if the given position is nearby to the Tile
        :param position: position to check
        :return: True if is nearby, False otherwise
        """
        directions = (-1, 0), (1, 0), (0, -1), (0, 1)
        return any(
            (self.position[0] + dx, self.position[1] + dy) == position
            for dx, dy in directions
        )

    def place_item(self, token_kind: str, token_species: str,
                   character: Character | None,  size_modifier: float = 1.0,
                   pos_modifier: tuple[float,float] = (0.0, 0.0),
                   bright_radius: float = 0.0, bright_int: float = 0.0, gradient: tuple [float,float] = (0.0,0.0)) -> None:
        """
        Places a Token on the Tile
        :param token_kind: Token.kind of the token to be placed
        :param token_species: Token.species of the token to be placed
        :param character: character (if any) associated with the token
        :param size_modifier: float indicating Token.shape.size scaling factor
        :param pos_modifier: tuple [float,float] indicating how many pixels (x, y) the Token.pos is shifted regarding
        :param bright_int: intensity of the brightness, from 0 (no brightness) to 1 (max brightness)
        :param bright_radius: radius of the illuminated area
        :param gradient: tuple indicating min and max steepness of brightness decrease with increase of distance
        from the center. Must range from 0 to 1. If different values, brightness flickers between those values. If
        equals, brightness is constant
        :return: None
        """
        token_args = {
            "kind": token_kind,
            "species": token_species,
            "position": self.position,
            "character": character,
            "dungeon_instance": self.dungeon,
            "size_modifier": size_modifier,
            "pos_modifier": pos_modifier,
            "pos": self.pos,
            "size": self.size,
            "bright_radius": bright_radius,
            "bright_int": bright_int,
            "gradient": gradient
        }

        match token_kind:
            case "player":
                token = PlayerToken(**token_args)
                character.token = token
            case "monster":
                token = MonsterToken(**token_args)
                character.token = token
            case "trap":
                token = SceneryToken(**token_args)
                character.token = token
            case _:
                token = SceneryToken(**token_args)

        self.set_token(token)
        self.bind(pos=self.update_tokens_pos)

    def check_if_enable(self, active_player: Player) -> bool:
        """
        Check if the Tile fulfills the requirements to be activated
        :param active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        if self.has_token("player"):
            return self._check_with_player_token(active_player)
        if self.has_token("wall"):
            return self._check_with_wall_token(active_player)

        # monsters have preference over traps
        if self.has_token("monster") and not self.get_token("monster").character.is_hidden:
                                          #or not self.has_token("trap")):
            return self._check_with_monster_token(active_player)
        if self.has_token("trap") and not self.get_token("trap").character.is_hidden: #and not self.has_token("monster"):
            return self._check_with_trap_token(active_player)
        #if self.has_token("monster") and self.has_token("trap"):
            #return self._check_with_monster_token(active_player) or self._check_with_trap_token(active_player)

        if active_player.using_dynamite:
            return (self.dungeon.check_if_connexion(active_player.token.position,
                                                    self.position,
                                                    [token_kind for token_kind in active_player.blocked_by
                                                     if token_kind != "trap"],  # traps do not block shooting
                                                    active_player.stats.shooting_range))
        else:
            # if characters are hidden will give connexion so no need to check within "check_with" methods
            return self.dungeon.check_if_connexion(active_player.token.position, self.position,
                                                   active_player.blocked_by, active_player.stats.remaining_moves)

    def _check_with_monster_token(self, active_player: Player) -> bool:
        """
        Checks if a Tile having a Token of Token.kind "monster" fulfills the requirements to be activated
        :param active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        if active_player.using_dynamite:
            return (self.dungeon.check_if_connexion(active_player.token.position,
                                                    self.position,
                                                    [token_kind for token_kind in active_player.blocked_by
                                                     if token_kind != "trap"],
                                                    active_player.stats.shooting_range))

        #if self.get_token("monster").character.is_hidden:
            #return True

        if self.is_nearby(active_player.get_position()):
            return active_player.can_fight(self.get_token("monster").species)

        return False

    def _check_with_wall_token(self, active_player: Player) -> bool:
        """
        Checks if a Tile having a Token of Token.kind "wall" fulfills the requirements to be activated
        :param active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        if active_player.using_dynamite:
            return (self.dungeon.check_if_connexion(active_player.token.position,
                                                    self.position,
                                                    [token_kind for token_kind in active_player.blocked_by
                                                     if token_kind != "trap"],
                                                    active_player.stats.shooting_range) and
            not self.has_token("wall","rock"))

        elif self.is_nearby(active_player.token.position) and not active_player.is_hidden:
            return active_player.can_dig(self.get_token("wall").species)

        return False

    def _check_with_player_token(self, active_player: Player) -> bool:
        """
        Checks if a Tile having a Token of Token.kind "player" fulfills the requirements to be activated
        :param active_player: active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        if active_player.using_dynamite:
            return False
        if self.get_token("player").character == active_player:
            return True
        if self.get_token("player").character.has_moved and not Monster.all_dead_or_out():
            return False

        return True

    def _check_with_trap_token(self, active_player: Player) -> bool:
        """
        Checks if a Tile having a Token of Token.kind "trap" fulfills the requirements to be activated
        :param active_player: active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        if active_player.using_dynamite:
            return (self.dungeon.check_if_connexion(active_player.token.position,
                                                    self.position,
                                                    [token_kind for token_kind in active_player.blocked_by
                                                     if token_kind != "trap"],
                                                    active_player.stats.shooting_range))

        #if self.get_token("trap").character.hidden:
            #return True
        if not self.get_token("trap").character.hidden and self.is_nearby(active_player.token.position):
            return True

        return False

    def on_release(self) -> None:
        """
        Handles the logic when a Player falls on the Tile.
        :return: None

        '''elif not any(self.has_token(token_kind) for token_kind in player.cannot_share_tile_with + ["trap"])\
                or (self.has_token("monster") and self.get_token("monster").character.is_hidden)\
                or (self.has_token("trap") and (self.get_token("trap").character.hidden or not player.can_disarm_trap)):'''

        """
        player = self.dungeon.game.active_character

        if self.has_token("player"):
            if self.get_token("player") == player.token:
                current_time = Clock.get_time()
                if self.first_click_time and current_time - self.first_click_time < self.double_click_interval:
                    self.first_click_time = None
                    player.perform_passive_action()
                else:
                    self.first_click_time = Clock.get_time()
                    return
            else:
                self.dungeon.game.switch_character(self.get_token("player").character)
            self.dungeon.game.update_switch("character_done")

        elif player.using_dynamite:
            player.throw_dynamite(self)
            # game.update_switch("character_done") at the end of self.dynamite_explode(). Here does not work

        # move player
        elif not any(self.has_token(token_kind) for token_kind in player.cannot_share_tile_with + ["trap"])\
             or (self.has_character and self.has_all_characters_hidden)\
             or (self.has_token("trap")
                 and not any(self.has_token(token_kind) for token_kind in player.cannot_share_tile_with)
                 and not player.can_disarm_trap):

            path = self.dungeon.find_shortest_path(
                player.token.position, self.position, player.blocked_by)
            player.token.slide(path, player.token.on_move_completed)

        else:
            player.act_on_tile(self)
            self.dungeon.game.update_switch("character_done")

    def dynamite_fall(self) -> None:
        """
        Handles the logic upon a dynamite fall on the Tile
        :return: None
        """
        if self.has_token("monster"):
            monster_token = self.get_token("monster")
            path = monster_token.character.get_path_to_target(
                monster_token.character.find_random_target(monster_token.character.stats.dodging_moves))
            if len(path) > 1 and monster_token.character.can_dodge:
                monster_token.select_character()
                monster_token.slide(path, on_complete=monster_token.on_dodge_completed)
            else:
                self.dynamite_explode()

        else:
            self.dynamite_explode()

    def dynamite_explode(self) -> None:
        """
        Handles the logic and the consequences of a dynamite explosion
        :return: None
        """
        has_light: bool = self.has_token("light")
        for token in self.tokens["monster"]:
            token.character.kill_character(self)
        self.delete_all_tokens()  # delete all pickables
        if has_light:  # no need to check all dungeon if tile has no torch
            self.dungeon.update_bright_spots()

        self.place_item("wall", "rock", None)
        self._show_explosion()
        self.dungeon.game.update_switch("character_done")

    def _show_explosion(self) -> None:
        """
        Shows an explosion on the Tile
        :return: None
        """
        with self.dungeon.canvas.after:
            ExplosionToken(pos=self.pos, size=self.size)

        if App.get_running_app().flickering_torches_on:
            self.dungeon.add_bright_spot(center=self.center,
                                        radius=self.width * 2,
                                        intensity=1.0,
                                        gradient=(0.95, 0.95),
                                        timeout=0,
                                        max_timeout=0.25)

