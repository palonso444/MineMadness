from __future__ import annotations

from kivy.uix.button import Button  # type: ignore
from kivy.clock import Clock

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
                tile.dungeon.level_start.remove(token.position)

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
        :return: None
        """
        return next((token for token in self.tokens[token_kind] if token.kind == token_kind))

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
            for token in token_list:
                token.delete_token(self)

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
                   character: Character | None,
                   size_modifier: float = 1.0, pos_modifier: tuple[float,float] = (0.0, 0.0)) -> None:
        """
        Places a Token on the Tile
        :param token_kind: Token.kind of the token to be placed
        :param token_species: Token.species of the token to be placed
        :param character: character (if any) associated with the token
        :param size_modifier: float indicating Token size modification regarding Tile.size
        :param pos_modifier: tuple indicating how many (Tile.height, Tile.width) times the Token.pos
        is shifted regarding Tile.pos (lower-left corner)
        if relation to Tile lower left corner (corresponding to default value (0.0, 0.0))
        :return: None
        """
        pos_modifier = self.width * pos_modifier[1], self.height * pos_modifier[0]  # order Tile.pos is (x,y)

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
        }

        if token_kind == "player":
            token = PlayerToken(**token_args)
            character.token = token
        elif token_kind == "monster":
            token = MonsterToken(**token_args)
            character.token = token
        else:
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
        if self.has_token("monster"):
            return self._check_with_monster_token(active_player)
        if self.has_token("wall"):
            return self._check_with_wall_token(active_player)

        path = self.dungeon.find_shortest_path(active_player.token.position, self.position, active_player.blocked_by)
        if 0 < len(path[1:]) <= active_player.stats.remaining_moves:
            return True
        return False

    def _check_with_monster_token(self, active_player: Player) -> bool:
        """
        Checks if a Tile having a Token of Token.kind "monster" fulfills the requirements to be activated
        :param active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        #tuple(item for item in active_player.blocked_by if item != "monster"),
        if active_player.using_dynamite:
            return self.dungeon.check_if_connexion(active_player.token.position,
                                                   self.position,
                                                   active_player.blocked_by,
                                                   active_player.stats.shooting_range)

        elif self.is_nearby(active_player.token.position):
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
                                            active_player.blocked_by,
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

    def on_release(self) -> None:
        """
        Handles the logic when a Player falls on the Tile.
        :return: None
        """
        player = self.dungeon.game.active_character

        if self.has_token("player"):
            if self.get_token("player") == player.token:
                current_time = Clock.get_time()
                if self.first_click_time and current_time - self.first_click_time < self.double_click_interval:
                    self.first_click_time = None
                    player.stats.remaining_moves = 0
                else:
                    self.first_click_time = Clock.get_time()
                    return
            else:
                self.dungeon.game.switch_character(self.get_token("player").character)
            self.dungeon.game.update_switch("character_done")

        elif player.using_dynamite:
            player.throw_dynamite(self)

        # TODO: make this more clear
        elif not any(self.has_token(token_kind) for token_kind in player.cannot_share_tile_with):
            path = self.dungeon.find_shortest_path(
                player.token.position, self.position, player.blocked_by)
            player.token.slide(path, player.token.on_move_completed)

        else:
            player.act_on_tile(self)

    def dynamite_fall(self) -> None:
        """
        Handles the logic upon a dynamite fall on the Tile
        :return: None
        """
        if self.has_token("monster"):
            monster_token = self.get_token("monster")
            path = monster_token.character.get_random_path(monster_token.character.stats.dodging_moves)
            if len(path) > 1 and monster_token.character.can_dodge:
                monster_token.slide(path, on_complete=monster_token.on_dodge_completed)
            else:
                monster_token.character.kill_character(self)
        self.delete_all_tokens()
        self.place_item("wall", "rock", None)
        self.show_explosion()

    def show_explosion(self) -> None:
        """
        Shows an explosion on the Tile
        :return: None
        """
        with self.dungeon.canvas.after:
            ExplosionToken(pos=self.pos, size=self.size)
