from __future__ import annotations

from kivy.graphics import Color
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.gridlayout import GridLayout

from collections import deque
from random import choice

import players
import monsters
from darkness_manager import DarknessManager
from player_class import Player
import trap_class as traps
import tile_classes as tiles
from game_stats import DungeonStats
from dungeon_blueprint import Blueprint
from tokens_solid import CharacterToken

# import cythonized_lights as cl

class DungeonLayout(GridLayout):
    """
    Class defining the board of the game. The level is determined by the MineMadnessGame class. The rest of
    features are determined by DungeonLayout.DungeonStats
    """

    positions_to_update = NumericProperty(0)
    damage_tokens = ListProperty([])  # list of currently acting DamageTokens in the whole dungeon

    def __init__(self, game: MineMadnessGame,
                 blueprint: Blueprint | None = None,
                 torches_dict: dict | None = None,
                 **kwargs):
        super().__init__(**kwargs)

        self.game: MineMadnessGame = game
        self.stats: DungeonStats = DungeonStats(self.game.level)
        self.rows: int = self.stats.size
        self.cols: int = self.stats.size
        self.total_gems: int = self.stats.gem_number

        if blueprint is None:
            self.blueprint: Blueprint = self._generate_blueprint(self.rows, self.cols)
        else:  # if game is loaded, blueprint is passed as argument
            self.blueprint = blueprint

        self.tiles_dict: dict[tuple, Tile] | None = None
        self.moving_token: CharacterToken | None = None  # CharacterTokens are not associated to any Tile while sliding

        self.dm: DarknessManager = DarknessManager(self, torches_dict=torches_dict)

    @staticmethod
    def on_damage_tokens(dungeon, damage_tokens) -> None:
        """
        When all DamageTokens in the dungeon are out, check if game over
        :return: None
        """
        if len(damage_tokens) == 0:
            dungeon.game.finish_game_or_finish_level()

    def _generate_blueprint(self, y_axis: int, x_axis: int) -> Blueprint:
        """
        Places items on DungeonLayout.blueprint depending on DungeonLayout.stats
        :param y_axis: length of y_axis of the blueprint
        :param x_axis: length of x_axis of the blueprint
        :return: complete blueprint of the dungeon
        """
        blueprint = Blueprint(y_axis, x_axis)
        if self.game.level == 1:
            player_chars: list[str] = ["%", "?", "&"]
        else:
            player_chars: list[str] = Player.get_alive_player_chars()
        blueprint.place_items_as_group(player_chars,  min_dist=1)
        blueprint.place_items(" ", 1)
        blueprint.place_items("o",  self.stats.gem_number)
        blueprint.place_items("t", self.stats.talisman_number)
        blueprint.place_items("d", self.stats.dynamite_number)
        blueprint.place_items("h", self.stats.powder_number)

        # add here elements to test
        # blueprint.place_items("%", 1)

        # comment these two lines to avoid adding elements to the dungeon
        for item, frequency in self.stats.level_progression().items():
            blueprint.place_items(item=item, number_of_items=int(frequency*blueprint.area))

        return blueprint

    def _set_tiles(self) -> None:
        """
        Initializes DungeonLayout.tiles.dict and prepares the floor of the dungeon, placing the exit and setting
        up characters
        :return: None
        """
        self.tiles_dict = {}

        for y in range(self.blueprint.y_axis):
            for x in range(self.blueprint.x_axis):

                if self.blueprint.has_item((y, x), " "):
                    tile: Tile = tiles.Tile(row=y, col=x, kind="exit", dungeon_instance=self)
                else:
                    tile: Tile = tiles.Tile(row=y, col=x, kind="floor", dungeon_instance=self)

                self.tiles_dict[tile.position] = tile
                self.add_widget(tile)

    def _place_tokens(self) -> None:
        """
        Places the tokens according to the blueprint and sets up the Token.character (if any)
        :return: None
        """
        for tile in self.children:

            tile_position = (tile.row, tile.col)
            character = None
            token_kind = None
            token_species = None
            if self.blueprint.has_item(tile_position, "%"):
                if self.game.level == 1 or self.game.advanced_start:
                    character = players.Sawyer()
                    character.setup_character(game=self.game)
                else:
                    character: Player = players.Player.data[0]
                    character.setup_for_new_level()
                token_kind = "player"
                token_species = "sawyer"

            elif self.blueprint.has_item(tile_position, "?"):
                if self.game.level == 1 or self.game.advanced_start:
                    character = players.Hawkins()
                    character.setup_character(game=self.game)
                else:
                    character: Player = Player.data[1]
                    character.setup_for_new_level()
                token_kind = "player"
                token_species = "hawkins"

            elif self.blueprint.has_item(tile_position, "&"):
                if self.game.level == 1 or self.game.advanced_start:
                    character = players.CrusherJane()
                    character.setup_character(game=self.game)
                else:
                    character: Player = Player.data[2]
                    character.setup_for_new_level()
                token_kind = "player"
                token_species = "crusherjane"

            if self.blueprint.has_item(tile_position, "K"):
                token_kind = "monster"
                token_species = "kobold"
                character: Monster = monsters.Kobold()

            elif self.blueprint.has_item(tile_position, "L"):
                token_kind = "monster"
                token_species = "lizard"
                character: Monster = monsters.BlindLizard()

            elif self.blueprint.has_item(tile_position, "B"):
                token_kind = "monster"
                token_species = "blackdeath"
                character = monsters.BlackDeath()

            elif self.blueprint.has_item(tile_position, "H"):
                token_kind = "monster"
                token_species = "hound"
                character: Monster = monsters.CaveHound()

            elif self.blueprint.has_item(tile_position, "G"):
                token_kind = "monster"
                token_species = "growl"
                character: Monster = monsters.Growl()

            elif self.blueprint.has_item(tile_position, "R"):
                token_kind = "monster"
                token_species = "golem"
                character: Monster = monsters.RockGolem()

            elif self.blueprint.has_item(tile_position, "O"):
                token_kind = "monster"
                token_species = "gnome"
                character: Monster = monsters.DarkGnome()

            elif self.blueprint.has_item(tile_position, "N"):
                token_kind = "monster"
                token_species = "nightmare"
                character: Monster = monsters.NightMare()

            elif self.blueprint.has_item(tile_position, "Y"):
                token_kind = "monster"
                token_species = "lindworm"
                character: Monster = monsters.LindWorm()

            elif self.blueprint.has_item(tile_position, "S"):
                token_kind = "monster"
                token_species = "shadow"
                character: Monster = monsters.WanderingShadow()

            elif self.blueprint.has_item(tile_position, "W"):
                token_kind = "monster"
                token_species = "wisp"
                character: Monster = monsters.DepthsWisp()

            elif self.blueprint.has_item(tile_position, "D"):
                token_kind = "monster"
                token_species = "djinn"
                character: Monster = monsters.MountainDjinn()

            elif self.blueprint.has_item(tile_position, "P"):
                token_kind = "monster"
                token_species = "pixie"
                character: Monster = monsters.Pixie()

            elif self.blueprint.has_item(tile_position, "V"):
                token_kind = "monster"
                token_species = "rattlesnake"
                character: Monster = monsters.RattleSnake()

            elif self.blueprint.has_item(tile_position, "A"):
                token_kind = "monster"
                token_species = "penumbra"
                character: Monster = monsters.Penumbra()

            elif self.blueprint.has_item(tile_position, "C"):
                token_kind = "monster"
                token_species = "clawjaw"
                character: Monster = monsters.ClawJaw()

            if self.blueprint.has_item(tile_position, "#"):
                token_kind = "wall"
                token_species = "rock"

            elif self.blueprint.has_item(tile_position, "{"):
                token_kind = "wall"
                token_species = "granite"

            elif self.blueprint.has_item(tile_position, "*"):
                token_kind = "wall"
                token_species = "quartz"

            if self.blueprint.has_item(tile_position, "p"):
                token_kind = "pickable"
                token_species = "shovel"

            elif self.blueprint.has_item(tile_position, "x"):
                token_kind = "pickable"
                token_species = "weapon"

            elif self.blueprint.has_item(tile_position, "j"):
                token_kind = "pickable"
                token_species = "jerky"

            elif self.blueprint.has_item(tile_position, "c"):
                token_kind = "pickable"
                token_species = "coffee"

            elif self.blueprint.has_item(tile_position, "l"):
                token_kind = "pickable"
                token_species = "tobacco"

            elif self.blueprint.has_item(tile_position, "w"):
                token_kind = "pickable"
                token_species = "whisky"

            elif self.blueprint.has_item(tile_position, "t"):
                token_kind = "pickable"
                token_species = "talisman"

            elif self.blueprint.has_item(tile_position, "h"):
                token_kind = "pickable"
                token_species = "powder"

            elif self.blueprint.has_item(tile_position, "d"):
                token_kind = "pickable"
                token_species = "dynamite"

            elif self.blueprint.has_item(tile_position, "o"):
                token_kind = "treasure"
                token_species = "gem"

            if self.blueprint.has_item(tile_position, "!"):
                token_kind = "trap"
                token_species = "trap"
                character: Trap = traps.Trap(game=self.game)

            if character is not None and character.kind == "monster":
                character.setup_character(game=self.game)  # Players are set up after matching blueprint

            # empty spaces ("." or " ") are None
            if token_kind is not None and token_species is not None:
                self.add_position_to_update(tile_position)
                tile.place_item(token_kind, token_species, character)

    def build_level(self) -> None:
        """
        Transforms the blueprint into a fully fledged level
        :return: None
        """
        self._set_tiles()
        self._place_tokens()
        # must be called here to properly save torch positions in MineMadnessApp.get_game_state()
        self.dm.place_torches(size_modifier=0.5)

    def unschedule_all_events(self) -> None:
        """
        Unschedules all events running in the background
        :return: None
        """
        if self.dm.flickering_torches is not None:
            self.dm.flickering_torches.cancel()
            self.dm.flickering_torches = None

        for tile in self.children:
            token: CharacterToken | None = None
            if tile.has_token("monster"):
                token = tile.get_token("monster")
            elif tile.has_token("player"):
                token = tile.get_token("player")
            if token is not None:
                token.effect_queue.clear()
            if self.moving_token is not None:
                self.moving_token.effect_queue.clear()
                self.moving_token.animation.cancel(self.moving_token)
                self.moving_token.animation = None
                self.moving_token = None

    @staticmethod
    def on_positions_to_update(dungeon: DungeonLayout, positions_to_update: list) -> None:
        """
        This function assigns DungeonLayout to the dungeon attribute of MineMadnessGame and starts the level.
        Triggered when all Tokens are positioned in their correct pos (level_start list is empty)
        :param dungeon: dungeon
        :param positions_to_update: list of token positions that need to be positioned. When empty, lever starts
        :return: None
        """
        if positions_to_update == 0:
            dungeon.dm.initialize_torches()
            dungeon.hide_penumbras()
            dungeon.game.dungeon = dungeon

            # if dungeon.bright_spots does not change its values, darkness must be cast manually
            if len(dungeon.dm.bright_spots) == 0:
                with dungeon.canvas.after:
                    # uncomment this to run the cythonized version
                    # dungeon.darkness = cl.generate_darkness_layer(dungeon, dungeon.darkness_intensity)
                    dungeon.darkness = dungeon.dm.generate_darkness_layer()

    def hide_penumbras(self) -> None:
        """
        Hides the penumbras Monster throughout the DungeonLayout (if any), if they have a
        Player within reachable range
        :return: None
        """
        for tile in self.children:
            if tile.has_token("monster", "penumbra"):
                character = tile.get_token("monster").character
                character.hide_if_player_in_range(character.stats.moves)  # remaining moves not yet established

    def restore_canvas_color(self, canvas: str) -> None:
        """
        Restores the canvas Color to the original state
        :param canvas: canvas to restore (before, after, canvas)
        :return: None
        """
        match canvas:
            case "canvas":
                canvas_context = self.canvas
            case "after":
                canvas_context = self.canvas.after
            case "before":
                canvas_context =  self.canvas.before
            case _:
                raise Exception(f"Invalid canvas argument {canvas}. Valid are: before, canvas, after.")

        with canvas_context:
            Color (1,1,1,1)

    @staticmethod
    def get_distance(position1: tuple[int:int], position2: tuple[int:int]) -> int:
        """
        Returns the distance (in number of steps) between 2 positions of the dungeon
        :param position1: first position
        :param position2: second position
        :return: distance between the two positions
        """
        return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

    @staticmethod
    def get_relative_position(position: tuple[int:int], target_position: tuple[int:int]) -> tuple[int, int]:
        """
        Returns the relative position of between the position and the target_position
        :param position: position of reference
        :param target_position: position whose relative position must be calculated
        :return: relative position. Examples: (-1, 0) -> up, (1, 0) -> down, (0, -1) -> left, (0, 1) -> right
        """
        return target_position[0] - position[0], target_position[1] - position[1]

    @staticmethod
    def are_nearby(position_1: tuple[int:int], position_2: tuple[int:int]) -> bool:
        """
        Checks if two positions in the dungeon have nearby positions
        :param position_1: first position
        :param position_2: second position
        :return: True if they are nearby, False otherwise
        """
        directions = (-1, 0), (1, 0), (0, -1), (0, 1)
        return any((position_1[0] + dx, position_1[1] + dy) == position_2 for dx, dy in directions)

    def check_if_connexion(self, position_1: tuple[int, int], position_2: tuple[int, int],
                           obstacles_kinds: list[str], num_of_steps: int) -> bool:
        """
        Checks if two positions of the DungeonLayout are connected or there are obstacles on the way that makes
        one inaccessible from the other in the given number of steps
        :param position_1: coordinates of the first position
        :param position_2: coordinates of the second position
        :param obstacles_kinds: Token.kinds of the obstacles to consider
        :param num_of_steps: maximum number of steps
        :return: True if there is a connexion, False otherwise
        """
        path = self.find_shortest_path(position_1, position_2, obstacles_kinds)
        # +1 added to steps as first position of the path is position_1, does not count
        return 1 < len(path) <= num_of_steps + 1

    def add_position_to_update(self, tile_position: tuple[int, int]) -> None:
        """
        Updates the counter of positions to update. Counter is decreased by Tile.update_tokens_pos() after updating
        Token.pos according to Tile.pos. When counter reaches 0, means that all Tokens are positioned in their
        respective pos and game can start.
        :param tile_position: position of the tile where Token must be positioned
        :return: None
        """
        if tile_position != (self.rows - 1, 0):  # position lower left corner does not need to be repositioned
            self.positions_to_update += 1

    def get_tile(self, position: tuple[int,int]) -> Tile:
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
        tile_positions: list = list(self.tiles_dict.keys())

        while tile_positions:
            tile = self.get_tile(choice(tile_positions))
            if free and tile.has_token():
                tile_positions.remove(tile.position)
            else:
                return tile

    def get_nearby_positions(self, position: tuple[int:int]) -> set[tuple[int, int]]:
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

    def get_nearby_spaces(self, position: tuple[int, int], token_kinds: list[str]) -> set[tuple[int, int]]:
        """
        Returns a set with positions that do not have tokens of the specified Token.kinds
        :param position: coordinates of the position from which we are interested to get nearby spaces
        :param token_kinds: list of Token.kind to avoid
        :return: set with nearby positions free of specified Token.kinds
        """
        return {position for position in self.get_nearby_positions(position)
                if all(not self.get_tile(position).has_token(token_kind)
                       for token_kind in token_kinds)}

    def check_within_limits(self, position: tuple[int, int]) -> bool:
        """
        Checks if a position lies within the limits of the dungeon
        :param position: position
        :return: True if lies within limits, False otherwise
        """
        return 0 <= position[0] < self.rows and 0 <= position[1] < self.cols

    def get_range(self, position: tuple[int, int], steps: int) -> set[tuple[int, int]]:
        """
        Returns a set with all the positions within a range defined by a central position and a number of steps
        :param position: coordinates of the central position of the range
        :param steps: number of steps from the central position
        :return: set with the coordinates of all positions within the range
        """
        mov_range: set = self._get_horizontal_range(position, steps)  # row where token is

        vertical_shift: int = 1
        for lateral_steps in range(steps, 0, -1):  # 0 is not inclusive but Token row is already added

            y_position: int = position[0] - vertical_shift  # move upwards
            if y_position >= 0:
                # lateral steps -1 because one character step is spent to go up or down
                mov_range = mov_range.union(self._get_horizontal_range((y_position, position[1]), lateral_steps - 1))

            y_position = position[0] + vertical_shift  # move downwards
            if y_position < self.rows:
                mov_range = mov_range.union(self._get_horizontal_range((y_position, position[1]), lateral_steps - 1))

            vertical_shift += 1

        return mov_range

    def _get_horizontal_range(self, position: tuple[int, int], lateral_steps: int) -> set[tuple[int, int]]:
        """
        Returns the coordinates of the positions within a row defined by a central position and a range of steps
        to each side
        :param position: central position of the row
        :param lateral_steps: number of steps to take to each side
        :return: set with all the coordinates within the row
        """
        horizontal_range: set = set()

        for step in range(0, lateral_steps + 1):
            if position[1] - step >= 0:
                horizontal_range.add((position[0], position[1] - step))  # add whole row left

            if position[1] + step < self.cols:
                horizontal_range.add((position[0], position[1] + step))  # add whole row right

        return horizontal_range

    def disable_all_tiles(self):
        """
        Disables all Tiles of the DungeonLayout
        :return: None
        """
        for tile in self.children:
            tile.disabled = True

    def enable_tiles(self, tile_positions: set[tuple[int:int]], active_character: Player) -> None:
        """
        Activates the Tiles within a range of positions
        :param tile_positions: coordinates of the tiles to activate if activable
        :param active_character: current active Player in the game
        :return: None
        """
        for position in tile_positions:
            tile = self.get_tile(position)
            tile.disabled = not tile.check_if_enable(active_character)

    def scan_tiles(self, token_kinds: list[str], exclude: bool = False) -> set[tuple[int:int]]:
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
                    any(tile.has_token(token) for token in token_kinds)}

    def find_shortest_path(
            self, start_tile_position: tuple[int, int], end_tile_position: tuple[int, int],
            excluded: list[str] | None = None
    ) -> list[tuple] | None:
        """
        Returns the shortest path from start_tile to end_tile in the form of list of positions
        e.g. [(0,1), (0,2), (1,2)]. Start tile positions and end tile positions included in path
        Returns start tile position if no possible path
        :param start_tile_position: coordinates of the starting tile
        :param end_tile_position: coordinates of the end tile
        :param excluded: Token.kinds that should be avoided as they block the path
        :return: path to target if possible, otherwise list with one element [start_tile_position]
        """
        directions: tuple = (-1, 0), (1, 0), (0, -1), (0, 1)
        queue: deque = deque(
            [(start_tile_position, [start_tile_position])]
        )

        excluded_positions: set[tuple] = {start_tile_position}
        if excluded is not None:
            excluded_positions = excluded_positions | self.scan_tiles(excluded)
        if end_tile_position in excluded_positions:
            excluded_positions.remove(end_tile_position)

        excluded_positions = self._filter_excluded_positions(excluded_positions)

        while len(queue) > 0:
            current_position, path = queue.popleft()

            if current_position == end_tile_position:
                return path

            for direction in directions:
                # explore one step in all 4 directions
                row, col = (current_position[0] + direction[0], current_position[1] + direction[1])

                if 0 <= row < self.rows and 0 <= col < self.cols and (row, col) not in excluded_positions:
                    excluded_positions.add((row, col))  # this may increase yield as it limits the number of paths
                    queue.append(((row, col), path + [(row, col)]))

        return [start_tile_position]

    def _filter_excluded_positions(self, excluded_positions: set[tuple]) -> set[tuple]:
        """
        Filters excluded positions depending on the game requirements
        :param excluded_positions: set of positions to filter
        :return: filtered positions
        """
        return {position for position in excluded_positions
                if not (tile := self.get_tile(position)).has_character
                or not tile.has_all_characters_hidden}

