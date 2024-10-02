from kivy.uix.gridlayout import GridLayout  # type: ignore
from kivy.properties import ListProperty
from collections import deque
from random import choice

import player_classes as players
import monster_classes as monsters
import token_classes as tokens
import tile_classes as tiles
from game_stats import DungeonStats
from dungeon_blueprint import Blueprint



class DungeonLayout(GridLayout):

    fading_tokens_items_queue = ListProperty([])

    def __init__(self, dungeon_level: int = 1, game=None, **kwargs):
        super().__init__(**kwargs)
        self.tiles_dict: dict[tuple : tiles.Tile] | None = None

        self.dungeon_level = dungeon_level
        self.stats = DungeonStats(self.dungeon_level)
        self.rows: int = self.stats.size()
        self.cols: int = self.stats.size()
        self.blueprint = self.generate_blueprint(self.rows, self.cols)

        # determines which character shows fadingtokens
        self.fading_token_character: players.Player | None = None
        # determines if tokens of Dungeon.fading_tokens_items_queue are displayed in green or red
        self.fading_tokens_effect_fades: bool | None = None

        self.game = game

    def display_depth(self):
        self.game.ids.level_label.text = (
            "Depth: " + str(self.dungeon_level * 30) + " ft."
        )

    def on_pos(self, *args):

        self.display_depth()  # dysplays depth in level_label of interface

        self.tiles_dict: dict[tuple : tiles.Tile] = (
            dict()
        )  # for faster access to tiles by get_tile()
        #self.blueprint = Blueprint(self.rows, self.cols,
                                   #self.determine_alive_players(), dungeon=self)
        self.game = self.parent.parent
        self.game.total_gems = 0

        for y in range(self.rows):
            for x in range(self.cols):
                position = y,x
                if self.blueprint.get_position(position) == "o":

                    self.game.total_gems += 1
                    tile = tiles.Tile(row=y, col=x, kind="floor", dungeon_instance=self)

                elif self.blueprint.get_position(position) == " ":

                    tile = tiles.Tile(row=y, col=x, kind="exit", dungeon_instance=self)

                else:

                    tile = tiles.Tile(row=y, col=x, kind="floor", dungeon_instance=self)

                self.tiles_dict[tile.position] = tile
                self.add_widget(tile)

        self.game.dungeon = self  # Adds dungeon as MineMadnessGame class attribute

    def generate_blueprint(self, height, width):

        blueprint = Blueprint(height, width)

        blueprint.place_items_as_group(self.determine_alive_players(), min_dist=1)

        blueprint.place_equal_items(" ", 1)
        blueprint.place_equal_items("o", self.stats.gem_number())

        for key, value in self.stats.level_progression().items():

            blueprint.place_items(
                item=key,
                frequency=value,
                protected=self.stats.mandatory_items,
            )

        #blueprint.print_map()
        return blueprint

    def determine_alive_players(self):

        if self.dungeon_level == 1:
            return players.Player.player_chars
            # return "&"
        else:
            live_players = set()
            for player in players.Player.exited:
                live_players.add(player.char)
            return live_players

    def match_blueprint(self):

        for tile in self.children:
            match self.blueprint.get_position((tile.row,tile.col)):

                case "%":
                    self.create_item(tile, "player", "sawyer")

                case "?":
                    self.create_item(tile, "player", "hawkins")

                case "&":
                    self.create_item(tile, "player", "crusherjane")

                case "K":
                    self.create_item(tile, "monster", "kobold")

                case "L":
                    self.create_item(tile, "monster", "lizard")

                case "B":
                    self.create_item(tile, "monster", "blackdeath")

                case "H":
                    self.create_item(tile, "monster", "hound")

                case "G":
                    self.create_item(tile, "monster", "growl")

                case "R":
                    self.create_item(tile, "monster", "golem")

                case "O":
                    self.create_item(tile, "monster", "gnome")

                case "N":
                    self.create_item(tile, "monster", "nightmare")

                case "Y":
                    self.create_item(tile, "monster", "lindworm")

                case "S":
                    self.create_item(tile, "monster", "shadow")

                case "W":
                    self.create_item(tile, "monster", "wisp")

                case "D":
                    self.create_item(tile, "monster", "djinn")

                case "P":
                    self.create_item(tile, "monster", "pixie")

                case "#":
                    self.create_item(tile, "wall", "rock")

                case "{":
                    self.create_item(tile, "wall", "granite")

                case "*":
                    self.create_item(tile, "wall", "quartz")

                case "p":
                    self.create_item(tile, "pickable", "shovel")

                case "x":
                    self.create_item(tile, "pickable", "weapon")

                case "j":
                    self.create_item(tile, "pickable", "jerky")

                case "c":
                    self.create_item(tile, "pickable", "coffee")

                case "l":
                    self.create_item(tile, "pickable", "tobacco")

                case "w":
                    self.create_item(tile, "pickable", "whisky")

                case "t":
                    self.create_item(tile, "pickable", "talisman")

                case "h":
                    self.create_item(tile, "pickable", "powder")

                case "d":
                    self.create_item(tile, "pickable", "dynamite")

                case "o":
                    self.create_item(tile, "pickable", "gem")

    def create_item(self, tile, token_kind, token_species):

        # this function cannot be a match due to function calls in between cases

        if token_kind == "player" or token_kind == "monster":

            if token_kind == "player":

                if token_species == "sawyer":

                    if self.dungeon_level == 1:
                        character = players.Sawyer()
                    else:
                        character = players.Player.transfer_player("Sawyer")

                elif token_species == "hawkins":

                    if self.dungeon_level == 1:
                        character = players.Hawkins()
                    else:
                        character = players.Player.transfer_player("Hawkins")

                elif token_species == "crusherjane":

                    if self.dungeon_level == 1:
                        character = players.CrusherJane()
                    else:
                        character = players.Player.transfer_player("Crusher Jane")

            elif token_kind == "monster":

                if token_species == "kobold":
                    character = monsters.Kobold()

                elif token_species == "lizard":
                    character = monsters.BlindLizard()

                elif token_species == "blackdeath":
                    character = monsters.BlackDeath()

                elif token_species == "hound":
                    character = monsters.CaveHound()

                elif token_species == "growl":
                    character = monsters.Growl()

                elif token_species == "golem":
                    character = monsters.RockGolem()

                elif token_species == "gnome":
                    character = monsters.DarkGnome()

                elif token_species == "nightmare":
                    character = monsters.NightMare()

                elif token_species == "lindworm":
                    character = monsters.LindWorm()

                elif token_species == "shadow":
                    character = monsters.WanderingShadow()

                elif token_species == "wisp":
                    character = monsters.DepthsWisp()

                elif token_species == "djinn":
                    character = monsters.MountainDjinn()

                elif token_species == "pixie":
                    character = monsters.Pixie()

            self.place_item(tile, token_kind, token_species, character)

        else:

            self.place_item(tile, token_kind, token_species)

    def place_item(
        self,
        tile: tiles.Tile,
        token_kind: str,
        token_species: str,
        character = None,
    ):

        if character is not None:

            character.position = tile.position
            character.dungeon = self
            character.id = len(character.__class__.data)
            character.__class__.data.append(character)

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

    def activate_which_tiles(self, tile_positions=None):

        for tile in self.children:
            # tile is not disabled if positions matches any in tile_positions and is activable
            tile.disabled = not (
                    tile_positions is not None and
                    any(tile.row == pos[0] and tile.col == pos[1] for pos in tile_positions) and
                    tile.is_activable
            )

    def get_tile(self, position):
        return self.tiles_dict.get(position)

    def scan(
        self, scenery: tuple , exclude: bool=False
    ):  # pass scenery as tuple of token.kinds to look for (e.g. ('wall', 'shovel'))

        if exclude:
            found_tiles = {tile.position for tile in self.children if
                           not any(tile.has_token((token, None)) for token in scenery)}
        else:
            found_tiles = {tile.position for tile in self.children if
                           any(tile.has_token((token, None)) for token in scenery)}

        return found_tiles

    def find_shortest_path(
        self, start_tile, end_tile, excluded=tuple()
    ) -> list[tuple] | None:
        """
        Returns the shortest path from start_tile to end_tile in the form of list of positions
        e.g. [(0,1), (0,2), (1,2)]. Start tile position NOT INCLUDED in path. End tile included.
        Returns None if there is no possible path.
        """

        directions: list[tuple] = [(-1, 0), (1, 0), (0, -1), (0, 1)]
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

    def get_surrounding_spaces(
        self, position: tuple[int], cannot_share_tile_with: tuple[str]
    ) -> set[tuple[int]]:
        """Returns surrounding positions of given position in which tiles are not occupied"""

        nearby_positions = self.get_nearby_positions(position)
        nearby_spaces = set()

        for position in nearby_positions:
            end_tile = self.get_tile(position)

            if not any(
                end_tile.has_token((token_kind, None))
                for token_kind in cannot_share_tile_with
            ):
                nearby_spaces.add(position)

        return nearby_spaces

    @staticmethod
    def are_nearby(item1, item2) -> bool:  # check if two positions are nearby
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for direction in directions:
            row, col = item1.position[0] + direction[0], item1.position[1] + direction[1]
            if (row, col) == item2.position:
                return True
        return False

    @staticmethod
    def get_distance(position1: tuple[int], position2: tuple[int]) -> int:
        return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])


    def get_nearby_positions(self, position: tuple[int]) -> set[tuple[int]]:
        """Returns surrounding positions"""

        nearby_positions = set()
        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))

        for direction in directions:

            if self.check_within_limits(
                (position[0] + direction[0], position[1] + direction[1])
            ):

                nearby_positions.add(
                    (position[0] + direction[0], position[1] + direction[1])
                )
        return nearby_positions

    def check_within_limits(self, position: tuple[int]) -> bool:

        return 0 <= position[0] < self.rows and 0 <= position[1] < self.cols

    def get_random_tile(self, free: bool = False):
        """
        Returns a random tile from the dungeon. If free, it will return a tile with no tokens
        """

        tiles_checked: set = set()
        total_tiles = len(self.children)

        while len(tiles_checked) < total_tiles:
            tile = choice(self.children)
            if free:
                if tile.has_token():
                    tiles_checked.add(self.children.index(tile))
                else:
                    return tile
            else:
                return tile

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
