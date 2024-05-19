from kivy.uix.gridlayout import GridLayout  # type: ignore

# from kivy.properties import BooleanProperty
# from kivy.graphics import Ellipse, Color

import crapgeon_utils as utils
import character_classes as characters
import token_classes as tokens
import tile_classes as tiles
from collections import deque
from random import randint


class DungeonLayout(GridLayout):  # initialized in kv file

    def dungeon_size(self):

        # return 6 + int(self.level / 1.5)
        return 3

    def gem_number(self):

        gem_number = int(self.level * 0.2)
        gem_number = 1 if gem_number < 1 else gem_number
        return gem_number

    def level_progression(self):

        wall_frequency = randint(20, 60) * 0.01

        monster_frequencies = {
            "K": 0.10 / self.level,
            "H": self.level * 0.015,
            "W": self.level * 0.006,
            "N": self.level * 0.002,
        }

        total_monster_frequency = sum(monster_frequencies.values())

        item_frequencies = {
            "#": wall_frequency,
            "p": wall_frequency * 0.15,
            "x": total_monster_frequency * 0.3,
            "j": self.level * 0.015,
        }

        all_frequencies = {**monster_frequencies, **item_frequencies}

        del monster_frequencies, item_frequencies
        return all_frequencies

    def on_pos(self, *args):

        self.generate_blueprint(self.rows, self.cols)  # initialize map of dungeon
        self.game = self.parent.parent
        self.game.total_gems = 0

        for y in range(self.rows):

            for x in range(self.cols):

                if self.blueprint[y][x] == "o":

                    self.game.total_gems += 1
                    tile = tiles.Tile(row=y, col=x, kind="floor", dungeon_instance=self)

                elif self.blueprint[y][x] == " ":

                    tile = tiles.Tile(row=y, col=x, kind="exit", dungeon_instance=self)

                else:

                    tile = tiles.Tile(row=y, col=x, kind="floor", dungeon_instance=self)

                self.add_widget(tile)

        self.game.dungeon = self  # Adds dungeon as CrapgeonGame class attribute

    def generate_blueprint(self, height, width):

        self.blueprint = utils.create_map(height, width)

        live_players = self.determine_alive_players()

        utils.place_items_as_group(self.blueprint, live_players, min_dist=1)

        # utils.place_equal_items(self.blueprint,'o', number_of_items=self.gem_number())
        utils.place_equal_items(self.blueprint, " ", 1)
        utils.place_equal_items(self.blueprint, "N", 1)
        # utils.place_equal_items(self.blueprint, "#", 10)
        utils.place_equal_items(self.blueprint, "o", 1)

        protected_items = ("%", "?", "&", " ", "o")

        # for key,value in self.level_progression().items():

        # utils.place_items (self.blueprint, item=key, frequency=value, protected = protected_items)

        # for y in range (len(self.blueprint)):
        # print (*self.blueprint[y])

    def determine_alive_players(self):

        if self.level == 1:
            # return characters.Player.player_chars
            return "&"
        else:
            live_players = set()
            for player in characters.Player.exited:
                live_players.add(player.char)
            return live_players

    def allocate_tokens(self):

        for tile in self.children:

            if self.blueprint[tile.row][tile.col] == "%":
                self.place_tokens(tile, "player", "sawyer")

            elif self.blueprint[tile.row][tile.col] == "?":
                self.place_tokens(tile, "player", "hawkins")

            elif self.blueprint[tile.row][tile.col] == "&":
                self.place_tokens(tile, "player", "crusherjane")

            elif self.blueprint[tile.row][tile.col] == "K":
                self.place_tokens(tile, "monster", "kobold")

            elif self.blueprint[tile.row][tile.col] == "H":
                self.place_tokens(tile, "monster", "hound")

            elif self.blueprint[tile.row][tile.col] == "W":
                self.place_tokens(tile, "monster", "wisp")

            elif self.blueprint[tile.row][tile.col] == "N":
                self.place_tokens(tile, "monster", "nightmare")

            elif self.blueprint[tile.row][tile.col] == "#":
                self.place_tokens(tile, "wall", "rock")

            elif self.blueprint[tile.row][tile.col] == "p":
                self.place_tokens(tile, "pickable", "shovel")

            elif self.blueprint[tile.row][tile.col] == "x":
                self.place_tokens(tile, "pickable", "weapon")

            elif self.blueprint[tile.row][tile.col] == "j":
                self.place_tokens(tile, "pickable", "jerky")

            elif self.blueprint[tile.row][tile.col] == "o":
                self.place_tokens(tile, "pickable", "gem")

    def place_tokens(self, tile, token_kind, token_species):

        if token_kind == "player" or token_kind == "monster":

            if token_kind == "player":

                if token_species == "sawyer":

                    if self.level == 1:
                        character = characters.Sawyer()
                    else:
                        character = characters.Player.transfer_player("Sawyer")

                elif token_species == "hawkins":

                    if self.level == 1:
                        character = characters.Hawkins()
                    else:
                        character = characters.Player.transfer_player("Hawkins")

                elif token_species == "crusherjane":

                    if self.level == 1:
                        character = characters.CrusherJane()
                    else:
                        character = characters.Player.transfer_player("Crusher Jane")

            elif token_kind == "monster":

                if token_species == "kobold":
                    character = characters.Kobold()

                elif token_species == "hound":
                    character = characters.CaveHound()

                elif token_species == "wisp":
                    character = characters.DepthsWisp()

                elif token_species == "nightmare":
                    character = characters.NightMare()

            tile.token = tokens.CharacterToken(
                kind=token_kind,
                species=token_species,
                dungeon_instance=self,
                pos=tile.pos,
                size=tile.size,
            )

            character.position = tile.position  # Character attributes initialized here
            character.token = tile.token
            character.dungeon = self

            character.id = len(character.__class__.data)
            character.__class__.data.append(character)

            tile.token.character = character

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

            tile.disabled = True

            if tile_positions:

                for position in tile_positions:

                    if (
                        tile.row == position[0]
                        and tile.col == position[1]
                        and tile.is_activable()
                    ):

                        tile.disabled = False

    def get_tile(self, position):

        for tile in self.children:

            if tile.position == position:

                return tile

    def scan(
        self, scenery, exclude=False
    ):  # pass scenery as tuple of token.kinds to look for (e.g. ('wall', 'shovel'))

        found_tiles = set()

        excluded_tiles = set()

        for tile in self.children:

            for token in scenery:

                if not exclude and tile.has_token_kind(token):

                    found_tiles.add(tile.position)

                elif exclude and tile.has_token_kind(token):

                    excluded_tiles.add(tile)

        if exclude:

            for tile in self.children:

                if tile not in excluded_tiles:

                    found_tiles.add(tile.position)

        return found_tiles

    def find_shortest_path(
        self, start_tile, end_tile, excluded=tuple()
    ) -> list[tuple] | None:

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = deque(
            [(start_tile.position, [])]
        )  # start_tile_pos is not included in the path

        excluded_positions = self.scan(excluded)
        excluded_positions.add(start_tile.position)
        if (
            start_tile.has_token_kind("monster")
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

    def show_damage_token(self, position, size):

        with self.canvas:

            tokens.DamageToken(pos=position, size=size, dungeon=self)

    def show_digging_token(self, position, size):

        with self.canvas:

            tokens.DiggingToken(pos=position, size=size, dungeon=self)
