from __future__ import annotations
from kivy.uix.gridlayout import GridLayout  # type: ignore
from collections import deque
from random import choice

import player_classes as players
import monster_classes as monsters
import solid_tokens as tokens
import tile_classes as tiles
from game_stats import DungeonStats
from dungeon_blueprint import Blueprint


class DungeonLayout(GridLayout):
    """
    Class defining the board of the game. The level is determined by the MineMadnessGame class. The rest of
    features are determined by DungeonLayout.DungeonStats
    """

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
    def are_nearby(position_1: tuple[int:int], position_2: tuple[int:int]) -> bool:
        """
        Checks if two positions in the dungeon have nearby positions
        :param position_1: first position
        :param position_2: second position
        :return: True if they are nearby, False otherwise
        """
        directions = (-1, 0), (1, 0), (0, -1), (0, 1)

        return any(
            (position_1[0] + dx, position_1[1] + dy) == position_2
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
        blueprint.place_equal_items("c", 3)
        blueprint.place_equal_items("w", 3)
        blueprint.place_equal_items("l", 3)
        blueprint.place_equal_items("O", 1)
        blueprint.place_equal_items("o", self.stats.gem_number())

        #for key, value in self.stats.level_progression().items():
            #blueprint.place_items(item=key, frequency=value, protected=self.stats.mandatory_items)

        #blueprint.print_map()
        return blueprint

    def match_blueprint(self) -> None:
        """
        Matches the symbols of the DungeonLayout.blueprint with the corresponding tokens and characters
        :return: None
        """
        for tile in self.children:
            tile_position = (tile.row,tile.col)
            character = None
            token_kind = None
            token_species = None
            match self.blueprint.get_position(tile_position):

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

            if character is not None:
                character.setup_character(position=tile_position, dungeon=self)

            # empty spaces ("." or " ") are None
            if token_kind is not None and token_species is not None:
                self.place_item(tile, token_kind, token_species, character)

    def place_item(self, tile: Tile, token_kind: str,
                   token_species: str, character: Character | None) -> None:
        """
        Places tokens on the tiles
        :param tile: tile in which item must be placed
        :param token_kind: Token.kind of the token to be placed
        :param token_species: Token.species of the token to be placed
        :param character: character (if any) associated with the token
        :return: None
        """
        token_args = {
            'kind': token_kind,
            'species': token_species,
            'character': character,
            'dungeon_instance': self,
            'pos': tile.pos,
            'size': tile.size,
        }

        if token_kind == "player":
            token = tokens.PlayerToken(**token_args)
            character.token = token
        elif token_kind == "monster":
            token = tokens.MonsterToken(**token_args)
            character.token = token
        else:
            token = tokens.SceneryToken(**token_args)

        tile.tokens[token_kind] = token
        tile.bind(pos=tile.update_tokens, size=tile.update_tokens)

    def get_tile(self, position: tuple [int:int]) -> Tile:
        """
        Returns the tile at the specified coordinates
        :param position: coordinates of the tile
        :return: tile at the specified coordinates
        """
        return self.tiles_dict.get(position)

    def get_random_tile(self, free: bool = False) -> Tile:
        """
        Returns a random tile from the dungeon
        :param free: bool specifying if the returned tile must be free (with no tokens)
        :return: random tile
        """
        tile_positions: list = self.tiles_dict.keys()

        while tile_positions:
            tile = self.get_tile(choice(tile_positions))
            if free and tile.has_token():
                tile.positions.remove(tile.position)
            else:
                return tile

    def get_nearby_positions(self, position: tuple[int:int]) -> set[tuple[int:int]]:
        """
        Returns the nearby positions of the specified position
        :param position: coordinates of the position
        :return: set of nearby positions
        """
        directions = (0, 1), (0, -1), (1, 0), (-1, 0)

        return {
            (position[0] + dx, position[1] + dy)
            for dx, dy in directions
            if self.check_within_limits((position[0] + dx, position[1] + dy))
        }

    def check_within_limits(self, position: tuple[int: int]) -> bool:
        """
        Checks if a position lies within the limits of the dungeon
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

    def scan_tiles(self, token_kinds: list[str], exclude: bool=False) -> set[tuple[int:int]]:
        """
        Returns a set with coordinates of tiles having none (exclude set to True) or at least one (exclude set to False)
        of Tokens of the specified token_kinds
        :param token_kinds: token kinds to scan
        :param exclude: determines if search is exclusive (returns coordinates of tiles NOT having
        any Token of the token_kinds provided) or inclusive (returns coordinates of tiles having at least a
        Token of ONE of the token_kind provided)
        :return: set with the coordinates of the tiles.
        """
        if exclude:
            return {tile.position for tile in self.children if
                           not any(tile.has_token(token) for token in token_kinds)}
        else:
            return {tile.position for tile in self.children if
                           any(tile.has_token(token) for token in token_kinds )}

    def find_shortest_path(
        self, start_tile_position, end_tile_position, excluded: list[str]|None = None
    ) -> list[tuple] | None:
        """
        Returns the shortest path from start_tile to end_tile in the form of list of positions
        e.g. [(0,1), (0,2), (1,2)]. Start tile position NOT INCLUDED in path. End tile included.
        Returns None if there is no possible path.
        """
        directions: tuple = (-1, 0), (1, 0), (0, -1), (0, 1)
        queue: deque = deque(
            [(start_tile_position, [])]
        )  # start_tile_pos is not included in the path

        excluded_positions = set()
        if excluded is not None:
            excluded_positions: set[tuple] = self.scan_tiles(excluded)
        excluded_positions.add(start_tile_position)

        if (
                self.get_tile(start_tile_position).has_token("monster")
            and end_tile_position in excluded_positions
        ):
            excluded_positions.remove(end_tile_position)

        while queue:

            current_position, path = queue.popleft()

            if current_position == end_tile_position:
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
