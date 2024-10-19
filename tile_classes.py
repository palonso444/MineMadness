from __future__ import annotations
from kivy.uix.button import Button  # type: ignore

# from kivy.animation import Animation
# from kivy.properties import Clock
# from kivy.graphics import Ellipse, Color

from monster_classes import Monster
from tokens_solid import SceneryToken, PlayerToken, MonsterToken


class Tile(Button):
    """
    Class defining each one of the Tiles of the DungeonLayout grid.
    """

    def __init__(self, row: int, col:int, kind: str, dungeon_instance: DungeonLayout, **kwargs):
        super().__init__(**kwargs)

        self.row: int = row
        self.col: int = col
        self.position: tuple[int,int] = row, col
        self.kind: str = kind
        self.tokens: dict [str:Token | None] = {
            "player": None,
            "monster": None,
            "wall": None,
            "pickable": None,
            "treasure": None
        }
        self.dungeon: DungeonLayout = dungeon_instance  # need to pass the instance of the dungeon to call dungeon.move_token from the class

    @staticmethod
    def update_tokens_pos(tile, tile_pos) -> None:
        """
        This callback updates the position of the Tokens when the pos of the Tile changes.
        :param tile: tile that changes the pos
        :param tile_pos: new pos value of the Tile
        :return: None
        """
        for token in tile.tokens.values():
            if token is not None:
                token.pos = tile_pos

    def set_token(self, token:Token) -> None:
        """
        Sets the specified Token as part of Tile.tokens
        :param token: Token to set
        :return: None
        """
        self.tokens[token.kind] = token

    def get_token(self, token_kind: str) -> Token:
        """
        Returns from Tile.tokens the Token of the specified kind
        :param token_kind: Token.kind of the Token
        :return: None
        """
        return self.tokens[token_kind]

    def remove_token(self, token:Token) -> None:
        """
        Removes from Tile.tokens the specified Token.
        :param token: Token to remove
        :return: None
        """
        self.tokens[token.kind] = None

    def delete_all_tokens(self) -> None:
        """
        Clears the Tile of all its Tokens
        :return: None
        """
        for token in self.tokens.values():
            if token is not None:
                print(self.position)
                print(token)
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
                raise ValueError("token_kind cannot be None and token_species not None")
            return any(token is not None for token in self.tokens.values())

        return (self.tokens[token_kind] is not None and
                (token_species is None or self.tokens[token_kind].species == token_species))

    def is_nearby(self, position: tuple[int,int]) -> bool:
        """
        Checks if the given position is nearby to the tile
        :param position: position to check
        :return: True if is nearby, False otherwise
        """
        directions = (-1, 0), (1, 0), (0, -1), (0, 1)

        return any(
            (self.position[0] + dx, self.position[1] + dy) == position
            for dx, dy in directions
        )

    def place_item(self, token_kind: str, token_species: str, character: Character | None) -> None:
        """
        Places tokens on the Tile
        :param token_kind: Token.kind of the token to be placed
        :param token_species: Token.species of the token to be placed
        :param character: character (if any) associated with the token
        :return: None
        """
        token_args = {
            'kind': token_kind,
            'species': token_species,
            'position': self.position,
            'character': character,
            'dungeon_instance': self.dungeon,
            'pos': self.pos,
            'size': self.size,
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

        return True

    def _check_with_monster_token(self, active_player: Player) -> bool:
        """
        Checks if a Tile having a Token of Token.kind "monster" has to be activated
        :param active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        if active_player.using_dynamite:
            return self.dungeon.check_if_connexion(active_player.token.position,
                                                   self.position,
                                                   tuple(item for item in active_player.blocked_by if item != "monster"),
                                                   active_player.stats.shooting_range)

        elif self.is_nearby(active_player.token.position):
            return active_player.can_fight(self.get_token("monster").species)

        return False

    def _check_with_wall_token(self, active_player: Player) -> bool:
        """
        Checks if a Tile having a Token of Token.kind "wall" has to be activated
        :param active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        if active_player.using_dynamite:
            return (self.dungeon.check_if_connexion(active_player.token.position,
                                            self.position,
                                            active_player.blocked_by,
                                            active_player.stats.shooting_range) and
            not self.has_token("wall","rock"))

        elif self.is_nearby(active_player.token.position):
            return active_player.can_dig(self.get_token("wall").species)

        return False

    def _check_with_player_token(self, active_player: Player) -> bool:
        """
        Checks if a Tile having a Token of Token.kind "player" has to be activated
        :param active_player: active_player: current active Player of the game
        :return: True if the Tile has to be activated, False otherwise
        """
        if active_player.using_dynamite:
            return False
        if self.get_token("player").character == active_player:
            return True
        if self.get_token("player").character.has_moved and not Monster.all_dead():
            return False

        return True

    def on_release(self):

        player = self.dungeon.game.active_character
        game = self.dungeon.game

        if player.using_dynamite:
            player.throw_dynamite()
            game.update_switch("ability_button")
            if self.has_token("monster"):
                self.get_token("monster").token_dodge()
            else:
                self.dynamite_fall()

        elif self.has_token("player") and self.get_token("player").character != player:
            game.switch_character(self.get_token("player").character)

        elif self.has_token("wall"):
            player.dig(self)
            game.update_switch("character_done")

        elif self.has_token("monster"):
            player.fight_on_tile(self)
            game.update_switch("character_done")

        else:
            start_tile = self.dungeon.get_tile(player.token.position)

            if start_tile.get_token("player").character == player:
                path = self.dungeon.find_shortest_path(
                    start_tile.get_token("player").position, self.position, start_tile.get_token("player").character.blocked_by)
                start_tile.get_token("player").move_token(path)

    def dynamite_fall(self) -> None:
        """
        Handles the logic upon a dynamite fall on the Tile
        :return: None
        """
        if self.has_token("monster"):
            self.get_token("monster").character.kill_character(self)
        self.delete_all_tokens()
        self.place_item("wall", "rock", None)
        #self.show_explosion()


    def show_explosion(self):
        """
        Shows an explosion
        """
        pass
        #with self.dungeon.canvas:
            #EffectToken("explosion", self.pos, self.size)
