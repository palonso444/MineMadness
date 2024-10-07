from __future__ import annotations
from kivy.uix.gridlayout import GridLayout  # type: ignore
from kivy.properties import ListProperty, NumericProperty
from collections import deque
from random import choice

import player_classes as players
import monster_classes as monsters
import token_classes as tokens
import tile_classes as tiles
from game_stats import DungeonStats
from dungeon_blueprint import Blueprint


class DungeonLayout(GridLayout):
    """
    Class defining the board of the game. The level is determined by the MineMadnessGame class. The rest of
    features are determined by DungeonLayout.DungeonStats
    """
    fading_tokens_items_queue = ListProperty([])

    def __init__(self, game: MineMadnessGame | None = None, **kwargs):
        super().__init__(**kwargs)

        # game is passed as argument from level 2 onwards
        if game is not None:
            self.game: MineMadnessGame = game
            self.dungeon_level: int = game.level
            self.stats: DungeonStats = DungeonStats(self.dungeon_level)
            self.rows: int = self.stats.size()
            self.cols: int = self.stats.size()
            self.blueprint: Blueprint = self.generate_blueprint(self.rows, self.cols)

        self.tiles_dict: dict[tuple: Tile] | None = None

        # determines which character shows fadingtokens
        self.fading_token_character: Player | None = None
        # determines if tokens of Dungeon.fading_tokens_items_queue are displayed in green or red
        self.fading_tokens_effect_fades: bool | None = None

    @staticmethod
    def get_distance(position1: tuple[int:int], position2: tuple[int:int]) -> int:
        """
        Returns the distance (in number of movements) between 2 positions of the dungeon
        :param position1: first position
        :param position2: second position
        :return: distance between the two positions
        """
        return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

    @staticmethod
    def are_nearby(item1: Token, item2: Token) -> bool:
        """
        Checks if two tokens in the dungeon have nearby positions
        :param item1: first item
        :param item2: second item
        :return: True if they are nearby, False otherwise
        """
        directions = (-1, 0), (1, 0), (0, -1), (0, 1)

        return any(
            (item1.position[0] + dx, item1.position[1] + dy) == item2.position
            for dx, dy in directions
        )

    @staticmethod
    def on_pos(dungeon: DungeonLayout, pos: list [int, int]) -> None:
        """
        Triggered when the dungeon is positioned the beginning of each level
        It initializes DungeonLayout.tiles.dict and prepares the floor of the dungeon, placing the exit
        :param dungeon: Instance of the dungeon corresponding to the current level
        :param pos: position (actual position on the screen) of the dungeon instance
        :return: None
        """
        dungeon.tiles_dict = dict ()

        for y in range(dungeon.blueprint.y_axis):
            for x in range(dungeon.blueprint.x_axis):

                if dungeon.blueprint.get_position((y,x)) == " ":
                    tile: Tile = tiles.Tile(row=y, col=x, kind="exit", dungeon_instance=dungeon)
                else:
                    tile: Tile = tiles.Tile(row=y, col=x, kind="floor", dungeon_instance=dungeon)

                dungeon.tiles_dict[tile.position] = tile
                dungeon.add_widget(tile)

        dungeon.game.dungeon = dungeon  # links dungeon with main (MineMadnessGame)

    def generate_blueprint(self, y_axis: int, x_axis: int) -> Blueprint:
        """
        Places items on DungeonLayout.blueprint depending on DungeonLayout.stats
        :param y_axis: length of y_axis of the blueprint
        :param x_axis: length of x_axis of the blueprint
        :return: complete blueprint of the dungeon
        """
        blueprint = Blueprint(y_axis, x_axis)

        blueprint.place_items_as_group(players.Player.get_alive_players(), min_dist=1)
        blueprint.place_equal_items(" ", 1)
        blueprint.place_equal_items("o", self.stats.gem_number())

        for key, value in self.stats.level_progression().items():
            blueprint.place_items(item=key, frequency=value, protected=self.stats.mandatory_items)

        #blueprint.print_map()
        return blueprint


    def match_blueprint(self):
        """
        Matches the symbols of the DungeonLayout.blueprint with the corresponding tokens and characters
        :return: None
        """
        for tile in self.children:
            character = None
            token_kind = None
            token_species = None
            match self.blueprint.get_position((tile.row,tile.col)):

                case "%":
                    if self.dungeon_level == 1:
                        token_kind = "player"
                        token_species = "sawyer"
                        character = players.Sawyer()
                    else:
                        character = players.Player.transfer_player("Sawyer")

                case "?":
                    if self.dungeon_level == 1:
                        token_kind = "player"
                        token_species = "hawkins"
                        character = players.Hawkins()
                    else:
                        character = players.Player.transfer_player("Hawkins")

                case "&":
                    if self.dungeon_level == 1:
                        token_kind = "player"
                        token_species = "crusherjane"
                        character = players.CrusherJane()
                    else:
                        character = players.Player.transfer_player("Crusher Jane")

                case "K":
                    token_kind="monster"
                    token_species = "kobold"
                    character = monsters.Kobold()

                case "L":
                    token_kind = "monster"
                    token_species = "lizard"
                    character = monsters.BlindLizard()

                case "B":
                    token_kind = "monster"
                    token_species = "blackdeath"
                    character = monsters.BlackDeath()

                case "H":
                    token_kind = "monster"
                    token_species = "hound"
                    character = monsters.CaveHound()

                case "G":
                    token_kind = "monster"
                    token_species = "growl"
                    character = monsters.Growl()

                case "R":
                    token_kind = "monster"
                    token_species = "golem"
                    character=monsters.RockGolem()

                case "O":
                    token_kind = "monster"
                    token_species = "gnome"
                    character=monsters.DarkGnome()

                case "N":
                    token_kind = "monster"
                    token_species = "nightmare"
                    character=monsters.NightMare()

                case "Y":
                    token_kind = "monster"
                    token_species = "lindworm"
                    character=monsters.LindWorm()

                case "S":
                    token_kind = "monster"
                    token_species = "shadow"
                    character=monsters.WanderingShadow()

                case "W":
                    token_kind = "monster"
                    token_species = "wisp"
                    character=monsters.DepthsWisp()

                case "D":
                    token_kind = "monster"
                    token_species = "djinn"
                    character=monsters.MountainDjinn()

                case "P":
                    token_kind = "monster"
                    token_species = "pixie"
                    character=monsters.Pixie()

                case "#":
                    token_kind = "wall"
                    token_species = "rock"

                case "{":
                    token_kind = "wall"
                    token_species = "granite"

                case "*":
                    token_kind = "wall"
                    token_species = "quartz"

                case "p":
                    token_kind = "pickable"
                    token_species = "shovel"

                case "x":
                    token_kind = "pickable"
                    token_species = "weapon"

                case "j":
                    token_kind = "pickable"
                    token_species = "jerky"

                case "c":
                    token_kind = "pickable"
                    token_species = "coffee"

                case "l":
                    token_kind = "pickable"
                    token_species = "tobacco"

                case "w":
                    token_kind = "pickable"
                    token_species = "whisky"

                case "t":
                    token_kind = "pickable"
                    token_species = "talisman"

                case "h":
                    token_kind = "pickable"
                    token_species = "powder"

                case "d":
                    token_kind = "pickable"
                    token_species = "dynamite"

                case "o":
                    token_kind = "pickable"
                    token_species = "gem"

            # empty spaces ("." or " ")
            if token_kind is not None and token_species is not None:
                self.place_item(tile, token_kind, token_species, character)


    def place_item(self, tile: Tile, token_kind: str,
                   token_species: str, character: Character | None):
        """
        Places tokens on the tiles
        :param tile: tile in which item must be placed
        :param token_kind: Token.kind of the token to be placed
        :param token_species: Token.species of the token to be placed
        :param character: character (if any) associated with the token
        :return: None
        """
        if character is not None:

            character.id = len(character.__class__.data)  # Delete __class__
            character.position = tile.position
            character.dungeon = self
            character.__class__.data.append(character)  # Delete __class__

            tile.token = tokens.CharacterToken(
                kind=token_kind,
                species=token_species,
                character=character,
                dungeon_instance=self,
                pos=tile.pos,
                size=tile.size,
            )

            character.token = tile.token

        else:

            tile.token = tokens.SceneryToken(
                kind=token_kind,
                species=token_species,
                dungeon_instance=self,
                pos=tile.pos,
                size=tile.size,
            )

        tile.bind(pos=tile.update_token, size=tile.update_token)

    def get_tile(self, position: tuple [int:int]) -> Tile:
        """
        Returns the tile at the specified coordinates
        :param position: coordinates of the tile
        :return: tile
        """
        return self.tiles_dict.get(position)

    def get_random_tile(self, free: bool = False) -> Tile:
        """
        Returns a random tile from the dungeon
        :param free: bool specifying if the returned tile must be free (with no tokens)
        :return: random tile
        """
        tiles_checked: set = set()
        total_tiles = len(self.children)

        while len(tiles_checked) < total_tiles:
            tile = choice(self.children)
            if free and tile.has_token():
                tiles_checked.add(self.children.index(tile))
                continue

            return tile

    def check_within_limits(self, position: tuple[int: int]) -> bool:
        """
        Check if a position lies within the limits of the dungeon
        :param position: position
        :return: True if lies within limits, False otherwise
        """
        return 0 <= position[0] < self.rows and 0 <= position[1] < self.cols

    def activate_which_tiles(self, tile_positions: list[tuple[int:int]] | None =None) -> None:
        """
        Activates the activable tiles within a range of positions
        :param tile_positions: coordinates of the tiles to activate if activable
        :return: None
        """
        for tile in self.children:
            # tile is not disabled if positions matches any in tile_positions and is tile.is_activable()
            tile.disabled = not (
                    tile_positions is not None and
                    any(tile.row == pos[0] and tile.col == pos[1] for pos in tile_positions) and
                    tile.is_activable
            )

    def scan(
        self, scenery: tuple , exclude: bool=False
    ):  # pass scenery as tuple of token.kinds to look for (e.g. ('wall', 'shovel'))

        if exclude:
            return {tile.position for tile in self.children if
                           not any(tile.has_token((token, None)) for token in scenery)}
        else:
            return {tile.position for tile in self.children if
                           any(tile.has_token((token, None)) for token in scenery)}

    def find_shortest_path(
        self, start_tile, end_tile, excluded=tuple()
    ) -> list[tuple] | None:
        """
        Returns the shortest path from start_tile to end_tile in the form of list of positions
        e.g. [(0,1), (0,2), (1,2)]. Start tile position NOT INCLUDED in path. End tile included.
        Returns None if there is no possible path.
        """

        directions: tuple = (-1, 0), (1, 0), (0, -1), (0, 1)
        queue: deque = deque(
            [(start_tile.position, [])]
        )  # start_tile_pos is not included in the path

        excluded_positions: set[tuple] = self.scan(excluded)
        excluded_positions.add(start_tile.position)
        if (
            start_tile.has_token(("monster", None))
            and end_tile.position in excluded_positions
        ):
            excluded_positions.remove(end_tile.position)

        while queue:

            current_position, path = queue.popleft()

            if current_position == end_tile.position:
                return path if len(path) > 0 else None

            for direction in directions:

                row, col = (
                    current_position[0] + direction[0],
                    current_position[1] + direction[1],
                )  # explore one step in all 4 directions

                if 0 <= row < self.rows and 0 <= col < self.cols:

                    if (row, col) not in excluded_positions:

                        excluded_positions.add((row, col))
                        queue.append(((row, col), path + [(row, col)]))

        return None

    def get_nearby_positions(self, position: tuple[int]) -> set[tuple[int:int]]:
        """Returns surrounding positions"""
        directions = (0, 1), (0, -1), (1, 0), (-1, 0)

        return {
            (position[0] + dx, position[1] + dy)
            for dx, dy in directions
            if self.check_within_limits((position[0] + dx, position[1] + dy))
        }

    def show_damage_token(self, position, size):

        with self.canvas:
            tokens.DamageToken(pos=position, size=size, dungeon=self)

    def show_digging_token(self, position, size):

        with self.canvas:
            tokens.DiggingToken(pos=position, size=size, dungeon=self)

    def show_effect_token(self, item: str, pos, size, effect_fades: bool = False):
        """
        Item is the item causing effect, see tokens.EffectToken class for more details.
        """

        with self.canvas:
            tokens.EffectToken(
                item=item, pos=pos, size=size, dungeon=self, effect_fades=effect_fades
            )

    def on_fading_tokens_items_queue(self, instance, queue):

        if len(queue) > 0:
            self.show_effect_token(
                self.fading_tokens_items_queue[0],
                self.fading_token_character.token.shape.pos,
                self.fading_token_character.token.shape.size,
                self.fading_tokens_effect_fades,
            )

    def remove_item_if_in_queue(self, instance, fading_token):

        if fading_token.item in self.fading_tokens_items_queue:
            self.fading_tokens_items_queue.remove(fading_token.item)
