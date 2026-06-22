from __future__ import annotations

from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.clock import Clock
from kivy.properties import ListProperty
from kivy.event import EventDispatcher
from kivy.app import App

from random import choice, uniform
from numpy import zeros, uint8, ogrid, int16, clip

class DarknessManager(EventDispatcher):
    """
    Manages the darkness layer covering the dungeon and the logic of torch placement and flickering
    """
    bright_spots = ListProperty([])

    def __init__(self, dungeon: DungeonLayout, **kwargs):
        super().__init__(**kwargs)
        self.dungeon: DungeonLayout = dungeon
        self.torches_dict: dict | None = None
        self.darkness: Rectangle | None = None
        self.darkness_intensity: int = 150  #  alpha intensity of the darkness. Must range from 0 to 255
        self.flickering_torches: ClockEvent | None = None
        self.darkness_text = None

        with self.dungeon.canvas.after:
            Rectangle(texture=self.darkness_text, pos=self.dungeon.pos, size=self.dungeon.size)

    def initialize_torches(self) -> None:
        """
        Places, rotates and initalizes the torches
        :return: None
        """
        self._place_torches(size_modifier=0.5)
        self._rotate_torches()
        self.update_bright_spots()

    def _setup_torches_dict(self) -> None:
        """
        Sets up the torches_dict. Keys are wall positions, values are list of pos_modifiers of all
        torches attached to that wall
        :return: None
        """
        wall_positions = self.dungeon.scan_tiles(["wall"])
        wall_free_positions = self.dungeon.scan_tiles(["wall"], exclude=True)

        all_torches_dict = {wall_position: [position for position in wall_free_positions
                                            if self.dungeon.are_nearby(wall_position, position)]
                            for wall_position in wall_positions}
        all_torches_dict = {key: value for key, value in all_torches_dict.items() if len(value) > 0}

        if len(all_torches_dict) > 0:
            torches_dict: dict = {key: [] for key in all_torches_dict.keys()}

            for _ in range(self.dungeon.stats.torch_number):
                random_key = choice(list(all_torches_dict.keys()))
                random_value = choice(all_torches_dict[random_key])
                torches_dict[random_key].append(self.dungeon.get_relative_position(random_key, random_value))
                all_torches_dict[random_key].remove(random_value)

                if len(all_torches_dict[random_key]) == 0:
                    del all_torches_dict[random_key]
                    if len(all_torches_dict) == 0:
                        break

            self.torches_dict = {key: value for key, value in torches_dict.items() if len(value) > 0}
        
    def _place_torches(self, size_modifier: float) -> None:
        """
        Sets up DungeonLayout.torches_dict and places torches depending on wall positions (torches are always
        attached to walls)
        :param size_modifier: modifier to apply to the original size of the torch (from 0 to 1, 1 being Tile.size)
        :return: None
        """
        if self.torches_dict is None:
            self._setup_torches_dict()
    
        tile_side = self.dungeon.get_random_tile().width
        torch_side = tile_side * size_modifier
        pos_modifier: tuple[float, float] | None = None
    
        if self.torches_dict is not None:
            for tile_position in self.torches_dict.keys():
                for relative_position in self.torches_dict[tile_position]:
                    match relative_position:  # relative positions (y, x), pos_modifiers (x, y)
                        case (-1, 0):
                            pos_modifier = (tile_side / 2 - torch_side / 2, -tile_side + torch_side)  # upper
                        case (1, 0):
                            pos_modifier = (tile_side / 2 - torch_side / 2, 0)  # lower
                        case (0, 1):
                            pos_modifier = (tile_side - torch_side, -tile_side / 2 + torch_side / 2)  # right
                        case (0, -1):
                            pos_modifier = (0, -tile_side / 2 + torch_side / 2)  # left
    
                    self.dungeon.add_position_to_update(tile_position)
                    tile = self.dungeon.get_tile(tile_position)
                    tile.place_item("light", "torch", character=None,
                                    size_modifier=size_modifier, pos_modifier=pos_modifier,
                                    bright_radius=tile.width * 2.5, bright_int=0.8, gradient=(0.45, 0.75))
 
    def _rotate_torches(self) -> None:
        """
        Rotates the torches depending on which side of the wall they are located. Must be called after updating
        torches.shape.pos as it needs the final Token.shape position to be established
        :return: None
        """
        for tile in self.dungeon.children:
            for token in tile.tokens["light"]:
                # pos_modifiers (x, y)
                if token.pos_modifier == (tile.width / 2 - token.size[0] / 2, -tile.width + token.size[0]):  # upper
                    token.rotate_token(degrees=180, axis=token.center)
    
                elif token.pos_modifier == (tile.width / 2 - token.size[0] / 2, 0):  # lower
                    pass
    
                elif token.pos_modifier == (tile.width - token.size[0], -tile.width / 2 + token.size[0] / 2):  # right
                    token.rotate_token(degrees=90, axis=token.center)
    
                elif token.pos_modifier == (0, -tile.width / 2 + token.size[0] / 2):  # left
                    token.rotate_token(degrees=270, axis=token.center)
                    
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
                                for tile in self.dungeon.children
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
    def on_bright_spots(dm: DarknessManager, bright_spots: list[dict]) -> None:
        """
        Callback triggered upon modification of DungeonLayout.bright_spots
        :param dm: DarknessManager instance
        :param bright_spots: list containing the center pos of all torches centers
        :return: None
        """
        if dm.flickering_torches is not None:
            dm.flickering_torches.cancel()

        if len(dm.bright_spots) > 0 and App.get_running_app().flickering_torches_on:
            dm.flickering_torches = Clock.schedule_interval(lambda dt: dm.darkness_flicker(dt=dt), 1 / 15)
        else:
            # if last bright spot is removed, cast static darkness
            if dm.darkness in dm.dungeon.canvas.after.children:
                dm.dungeon.canvas.after.remove(dm.darkness)

            with dm.dungeon.canvas.after:
                # uncomment this to run the cythonized version
                # dungeon.darkness = cl.generate_darkness_layer(dungeon, dungeon.darkness_intensity)
                dm.darkness = dm.generate_darkness_layer()
    
    def darkness_flicker(self, dt: float) -> None:
        """
        Wrapper function that generates a darkness with flickering brightness points. Needs to be scheduled
        using Clock.schedule_interval() and specifying the desired frequency
        :param dt: delta time
        :return: None
        """
        for bright_spot in self.bright_spots:
            if bright_spot["timeout"] is not None:
                bright_spot["timeout"] += dt
                if bright_spot["timeout"] > bright_spot["max_timeout"]:
                    self.bright_spots.remove(bright_spot)

        if self.darkness in self.dungeon.canvas.after.children:
            self.dungeon.canvas.after.remove(self.darkness)

        with self.dungeon.canvas.after:
            # uncomment this to run the cythonized version
            # self.darkness = cl.generate_darkness_layer(self, alpha_intensity)
            self.darkness = self.generate_darkness_layer()

    def generate_darkness_layer(self) -> Rectangle:
        """
        **********************************************************************************
        THIS FUNCTION HAS BEEN CYTHONIZED -- SEE cythonized_lights.pyx
        **********************************************************************************
        Generates a darkness layer with optional illuminated areas
        :return: darkness layer to be displayed on the canvas
        """
        # texture = Texture.create(size=self.dungeon.size, colorfmt="rgba")
        if self.darkness_text is None:
            self.create_text()

        data = zeros((self.darkness_text.height, self.darkness_text.width, 4), dtype=uint8)
        data[:, :, 3] = self.darkness_intensity

        for bright_spot in self.bright_spots:
            gradient = uniform(bright_spot["gradient"][0], bright_spot["gradient"][1])
            #max_distance = bright_spot["radius"] ** 2
            #y_pos, x_pos = ogrid[:self.darkness_text.height, :self.darkness_text.width]  # grid of coordinates of all pixels

            #distance_from_center = (x_pos - bright_spot["center"][0]) ** 2 + (y_pos - bright_spot["center"][1]) ** 2
            #light_mask = (distance_from_center < max_distance)  # [bool] array
            brightness = ((1 - (distance_from_center[light_mask] / max_distance) ** gradient)
                          * self.darkness_intensity * bright_spot["intensity"])

            temp_data = data[light_mask, 3].astype(int16) - brightness.astype(int16)
            data[light_mask, 3] = clip(temp_data, 0, self.darkness_intensity).astype(uint8)

        self.darkness_text.blit_buffer(data.flatten(), colorfmt="rgba", bufferfmt="ubyte")

        return Rectangle(texture=self.darkness_text, pos=self.dungeon.pos, size=self.dungeon.size)

    def create_text(self):
        self.darkness_text = Texture.create(size=self.dungeon.size, colorfmt="rgba")

        #with self.dungeon.canvas.after:
            #self.darkness = Rectangle(texture=self.darkness_text, pos=self.dungeon.pos, size=self.dungeon.size)

    def precompute_bright_spots(self):
        for bright_spot in self.bright_spots:
            max_distance = bright_spot["radius"] ** 2
            y_pos, x_pos = ogrid[:self.darkness_text.height, :self.darkness_text.width]  # grid of coordinates of all pixels

            distance_from_center = (x_pos - bright_spot["center"][0]) ** 2 + (y_pos - bright_spot["center"][1]) ** 2
            light_mask = (distance_from_center < max_distance)  # [bool] array


