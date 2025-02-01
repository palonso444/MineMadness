from __future__ import annotations

from kivy.graphics import Rectangle, Color
from kivy.properties import NumericProperty, ListProperty
from kivy.uix.gridlayout import GridLayout  # type: ignore
from kivy.graphics.texture import Texture
from kivy.clock import Clock

from collections import deque
from random import choice, uniform
from numpy import uint8, int16, ogrid, zeros, clip

import player_classes as players
import monster_classes as monsters
import trap_class as traps
import tile_classes as tiles
from game_stats import DungeonStats
from dungeon_blueprint import Blueprint


class DungeonLayout(GridLayout):
    """
    Class defining the board of the game. The level is determined by the MineMadnessGame class. The rest of
    features are determined by DungeonLayout.DungeonStats
    """

    positions_to_update = NumericProperty(0)
    bright_spots = ListProperty([])

    def __init__(self, game: MineMadnessGame,
                 blueprint: Blueprint | None = None,
                 torches_dict: dict[tuple:[list]] | None = None,
                 **kwargs):
        super().__init__(**kwargs)

        self.game: MineMadnessGame = game
        self.dungeon_level: int = game.level
        self.stats: DungeonStats = DungeonStats(self.dungeon_level)
        self.rows: int = self.stats.size
        self.cols: int = self.stats.size
        if blueprint is None:
            self.blueprint: Blueprint = self.generate_blueprint(self.rows, self.cols)
        else:
            self.blueprint = blueprint

        self.tiles_dict: dict[tuple: Tile] | None = None

        self.torches_dict: dict[tuple:list] | None = torches_dict
        self.darkness: Rectangle | None = None
        self.flickering_lights: ClockEvent | None = None

    def _setup_torches_dict(self) -> None:
        """
        Sets up the DungeonLayout.torches_dict. Keys are wall positions, values are list of pos_modifiers of all
        torches attached to that wall
        :return: None
        """
        wall_positions = self.scan_tiles(["wall"])
        wall_free_positions = self.scan_tiles(["wall"], exclude=True)

        all_torches_dict = {wall_position: [position for position in wall_free_positions
                                            if self.are_nearby(wall_position, position)]
                            for wall_position in wall_positions}
        all_torches_dict = {key: value for key, value in all_torches_dict.items() if len(value) > 0}

        if len(all_torches_dict) > 0:
            torches_dict: dict = {key: [] for key in all_torches_dict.keys()}

            for _ in range(self.stats.torch_number):
                random_key = choice(list(all_torches_dict.keys()))
                random_value = choice(all_torches_dict[random_key])
                torches_dict[random_key].append(self.get_relative_position(random_key, random_value))
                all_torches_dict[random_key].remove(random_value)

                if len(all_torches_dict[random_key]) == 0:
                    del all_torches_dict[random_key]
                    if len(all_torches_dict) == 0:
                        break

            self.torches_dict = {key: value for key, value in torches_dict.items() if len(value) > 0}

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
            dungeon._rotate_torches()
            dungeon.update_bright_spots()
            dungeon.hide_penumbras()
            dungeon.game.dungeon = dungeon

            # if dungeon.bright_spots does not change its values, darkness must be cast manually
            if len(dungeon.bright_spots) == 0:
                dungeon.cast_darkness(alpha_intensity=150)

    def update_bright_spots(self) -> None:
        """
        Stores in DungeonLayout.bright_spots one bright spot dict for each Token with bright_intensity > 0
        :return: None
        """
        current_bright_spots = self.bright_spots[:]

        self.bright_spots = ([{"center": token.center,
                               "radius": token.bright_radius,
                               "intensity": token.bright_int,
                               "gradient": token.gradient,
                               "timeout": None,
                               "max_timeout": None}
                              for tile in self.children
                              for token_list in tile.tokens.values()
                              for token in token_list if token.bright_int > 0]

                             +

                             [bright_spot for bright_spot in current_bright_spots if
                              bright_spot["max_timeout"] is not None])

    def add_bright_spot(self, center: tuple[float, float], radius: float, intensity: float,
                       gradient: tuple[float, float], timeout: float | None, max_timeout: float | None) -> None:
        """
        Adds a single bright spot dict to DungeonLayout.bright_spots
        :return: None
        """
        self.bright_spots.append({key: value for key, value in locals().items() if key != "self"})

    @staticmethod
    def on_bright_spots(dungeon: DungeonLayout, bright_spots: list[dict]) -> None:
        """
        Callback triggered upon modification of DungeonLayout.bright_spots
        :param dungeon: DungeonLayout instance
        :param bright_spots: list containing the center pos of all torches centers
        :return: None
        """
        if dungeon.flickering_lights is not None:
            dungeon.flickering_lights.cancel()

        dungeon.flickering_lights = Clock.schedule_interval(lambda dt: dungeon.darkness_flicker(alpha_intensity=150,
                                                                                                dt=dt),
                                                                                                1 / 15)
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

        return any(
            (position_1[0] + dx, position_1[1] + dy) == position_2
            for dx, dy in directions
        )

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

    @staticmethod
    def on_pos(dungeon: DungeonLayout, pos: list[int, int]) -> None:
        """
        Triggered when the dungeon is positioned the beginning of each level
        It initializes DungeonLayout.tiles.dict and prepares the floor of the dungeon, placing the exit
        :param dungeon: Instance of the dungeon corresponding to the current level
        :param pos: position (actual position on the screen) of the dungeon instance
        :return: None
        """
        dungeon.tiles_dict = dict()

        for y in range(dungeon.blueprint.y_axis):
            for x in range(dungeon.blueprint.x_axis):

                if dungeon.blueprint.get_position((y, x)) == " ":
                    tile: Tile = tiles.Tile(row=y, col=x, kind="exit", dungeon_instance=dungeon)
                else:
                    tile: Tile = tiles.Tile(row=y, col=x, kind="floor", dungeon_instance=dungeon)

                dungeon.tiles_dict[tile.position] = tile
                dungeon.add_widget(tile)

        dungeon.match_blueprint()
        dungeon.place_torches(size_modifier=0.5)

    def generate_blueprint(self, y_axis: int, x_axis: int) -> Blueprint:
        """
        Places items on DungeonLayout.blueprint depending on DungeonLayout.stats
        :param y_axis: length of y_axis of the blueprint
        :param x_axis: length of x_axis of the blueprint
        :return: complete blueprint of the dungeon
        """
        blueprint = Blueprint(y_axis, x_axis)
        self.stats.stats_level = 16
        blueprint.place_items_as_group(players.Player.get_surviving_players(), min_dist=1)
        blueprint.place_items(" ", 1)
        blueprint.place_items("o", self.stats.gem_number)

        for item, frequency in self.stats.level_progression().items():
            blueprint.place_items(item=item, number_of_items=int(frequency*blueprint.area))

        blueprint.purge_blueprint(max_total_frequency=0.6,
                                  protected={" ", "o", "&", "%", "?", "o", "#", "{", "*", "!", "t"})
        #blueprint.print_map()
        return blueprint

    def darkness_flicker(self, alpha_intensity: int, dt: float) -> None:
        """
        Wrapper function that generates a darkness with flickering brightness points. Needs to be scheduled
        using Clock.schedule_interval() and specifying the desired frequency
        :param alpha_intensity: alpha intensity of the darkness. Must range from 0 to 255
        :param dt: delta time
        :return: None
        """
        for bright_spot in self.bright_spots:
            if bright_spot["timeout"] is not None:
                bright_spot["timeout"] += dt
                if bright_spot["timeout"] > bright_spot["max_timeout"]:
                    self.bright_spots.remove(bright_spot)

        if self.darkness in self.canvas.after.children:
            self.canvas.after.remove(self.darkness)

        self.cast_darkness(alpha_intensity=alpha_intensity)

    def cast_darkness(self, alpha_intensity: int) -> None:
        """
        Wrapper method to cast a darkness layer on DungeonLayout.canvas
        :param alpha_intensity: alpha intensity of the darkness layer
        :return: None
        """
        with self.canvas.after:
            self.darkness = self._generate_darkness_layer(alpha_intensity=alpha_intensity)

    def _generate_darkness_layer(self, alpha_intensity: int) -> Rectangle:
        """
        Generates a darkness layer with optional illuminated areas
        :param alpha_intensity: alpha intensity of the darkness. Must range from 0 to 255
        :return: darkness layer to be displayed on the canvas
        """
        texture = Texture.create(size=self.size, colorfmt="rgba")
        data = zeros((texture.height, texture.width, 4), dtype=uint8)
        data[:, :, 3] = alpha_intensity

        for bright_spot in self.bright_spots:
            gradient = uniform(bright_spot["gradient"][0], bright_spot["gradient"][1])
            max_distance = bright_spot["radius"] ** 2
            y_pos, x_pos = ogrid[:texture.height, :texture.width]  # grid of coordinates of all pixels

            distance_from_center = (x_pos - bright_spot["center"][0]) ** 2 + (y_pos - bright_spot["center"][1]) ** 2
            light_mask = (distance_from_center < max_distance)  # [bool] array
            brightness = ((1 - (distance_from_center[light_mask] / max_distance) ** gradient)
                          * alpha_intensity * bright_spot["intensity"])

            temp_data = data[light_mask, 3].astype(int16) - brightness.astype(int16)
            data[light_mask, 3] = clip(temp_data, 0, alpha_intensity).astype(uint8)

        texture.blit_buffer(data.flatten(), colorfmt="rgba", bufferfmt="ubyte")

        return Rectangle(texture=texture, pos=self.pos, size=self.size)

    def _add_position_to_update(self, tile_position: tuple[int, int]) -> None:
        """
        Updates the counter of positions to update. Counter is decreased by Tile.update_tokens_pos() after updating
        Token.pos according to Tile.pos. When counter reaches 0, means that all Tokens are positioned in their
        respective pos and game can start.
        :param tile_position: position of the tile where Token must be positioned
        :return: None
        """
        if tile_position != (self.rows - 1, 0):  # position lower left corner does not need to be repositioned
            self.positions_to_update += 1

    def place_torches(self, size_modifier: float) -> None:
        """
        Sets up DungeonLayout.torches_dict and places torches depending on wall positions (torches are always
        attached to walls)
        :param size_modifier: modifier to apply to the original size of the torch (from 0 to 1, 1 being Tile.size)
        :return: None
        """
        if self.torches_dict is None:
            self._setup_torches_dict()

        tile_side = self.get_random_tile().width
        torch_side = tile_side * size_modifier
        pos_modifier: tuple[float, float] | None = None

        if self.torches_dict is not None:
            for tile_position in self.torches_dict.keys():
                for relative_position in self.torches_dict[tile_position]:
                    match relative_position:  # relative positions (y, x), pos_modifiers (x, y)
                        case (-1, 0):
                            pos_modifier = (tile_side / 2 - torch_side / 2,
                                            -tile_side + torch_side)  # upper
                        case (1, 0):
                            pos_modifier = (tile_side / 2 - torch_side / 2,
                                            0)  # lower
                        case (0, 1):
                            pos_modifier = (tile_side - torch_side,
                                            -tile_side / 2 + torch_side / 2)  # right
                        case (0, -1):
                            pos_modifier = (0,
                                            -tile_side / 2 + torch_side / 2)  # left

                    self._add_position_to_update(tile_position)
                    tile = self.get_tile(tile_position)
                    tile.place_item("light", "torch", character=None,
                                    size_modifier=size_modifier, pos_modifier=pos_modifier,
                                    bright_radius=tile.width * 2.5, bright_int=0.8, gradient = (0.45, 0.75))

    def _rotate_torches(self) -> None:
        """
        Rotates the torches depending on which side of the wall they are located. Must be called after updating
        torches.shape.pos as it needs the final Token.shape position to be established
        :return: None
        """
        for tile in self.children:
            for token in tile.tokens["light"]:
                # pos_modifiers (x, y)
                if token.pos_modifier == (tile.width / 2 - token.size[0] / 2,
                                          -tile.width + token.size[0]):  # upper
                    token.rotate_token(degrees=180, axis=token.center)

                elif token.pos_modifier == (tile.width / 2 - token.size[0] / 2,
                                            0):  # lower
                    pass

                elif token.pos_modifier == (tile.width - token.size[0],
                                            -tile.width / 2 + token.size[0] / 2):  # right
                    token.rotate_token(degrees=90, axis=token.center)

                elif token.pos_modifier == (0,
                                            -tile.width / 2 + token.size[0] / 2):  # left
                    token.rotate_token(degrees=270, axis=token.center)

    def match_blueprint(self) -> None:
        """
        Matches the symbols of the DungeonLayout.blueprint with the corresponding tokens and characters
        :return: None
        """
        for tile in self.children:
            tile_position = (tile.row, tile.col)
            character = None
            token_kind = None
            token_species = None
            match self.blueprint.get_position(tile_position):

                case "%":
                    if self.dungeon_level == 1:
                        character = players.Sawyer()
                    else:
                        character = players.Player.transfer_player("sawyer")
                    token_kind = "player"
                    token_species = "sawyer"

                case "?":
                    if self.dungeon_level == 1:
                        character = players.Hawkins()
                    else:
                        character = players.Player.transfer_player("hawkins")
                    token_kind = "player"
                    token_species = "hawkins"

                case "&":
                    if self.dungeon_level == 1:
                        character = players.CrusherJane()
                    else:
                        character = players.Player.transfer_player("crusherjane")
                    token_kind = "player"
                    token_species = "crusherjane"

                case "K":
                    token_kind = "monster"
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
                    character = monsters.RockGolem()

                case "O":
                    token_kind = "monster"
                    token_species = "gnome"
                    character = monsters.DarkGnome()

                case "N":
                    token_kind = "monster"
                    token_species = "nightmare"
                    character = monsters.NightMare()

                case "Y":
                    token_kind = "monster"
                    token_species = "lindworm"
                    character = monsters.LindWorm()

                case "S":
                    token_kind = "monster"
                    token_species = "shadow"
                    character = monsters.WanderingShadow()

                case "W":
                    token_kind = "monster"
                    token_species = "wisp"
                    character = monsters.DepthsWisp()

                case "D":
                    token_kind = "monster"
                    token_species = "djinn"
                    character = monsters.MountainDjinn()

                case "P":
                    token_kind = "monster"
                    token_species = "pixie"
                    character = monsters.Pixie()

                case "V":
                    token_kind = "monster"
                    token_species = "rattlesnake"
                    character = monsters.RattleSnake()

                case "A":
                    token_kind = "monster"
                    token_species = "penumbra"
                    character = monsters.Penumbra()

                case "C":
                    token_kind = "monster"
                    token_species = "clawjaw"
                    character = monsters.ClawJaw()

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
                    token_kind = "treasure"
                    token_species = "gem"

                case "!":
                    token_kind = "trap"
                    token_species = "trap"
                    character = traps.Trap()

            if character is not None:
                character.setup_character()

            # empty spaces ("." or " ") are None
            if token_kind is not None and token_species is not None:
                self._add_position_to_update(tile_position)
                tile.place_item(token_kind, token_species, character)

    def get_tile(self, position: tuple[int:int]) -> Tile:
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

