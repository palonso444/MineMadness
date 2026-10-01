from __future__ import annotations
from dataclasses import dataclass

import numpy as np
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.app import App

from tokens_solid import BrightArea

from random import choice, uniform
from numpy import zeros, uint8, ogrid, int16, clip

@dataclass
class DarknessLayer:
    """
    Dataclass defining a darkness layer.
    """
    texture: Rectangle
    pixel_int_data: ndarray
    light_data: ndarray
    bright_areas: list[BrightArea]
    flicker_mods: dict[int, float]  # key: brightArea id, value: flicker_mod

class DarknessManager(EventDispatcher):
    """
    Manages the darkness layer covering the dungeon and the logic of torch placement and flickering. Updating the list
    DarknessManager.bright_areas triggers generation of new darkness layers considering all tokens with bright_int > 0
    """

    def __init__(self, dungeon: DungeonLayout, torches_dict: dict | None, **kwargs):
        super().__init__(**kwargs)
        self.dungeon: DungeonLayout = dungeon
        self.bright_areas: list[BrightArea] | None = None
        self.torches_dict: dict | None = torches_dict
        self.flickering_torches: ClockEvent | None = None

        self.darkness_intensity: int = 150  # alpha intensity of the darkness. Must range from 0 to 255
        self.number_of_layers: int = 10  # number of darkness layers available in list
        self.darkness: DarknessLayer | None = None
        self.darkness_layers: list[DarknessLayer] | None = None

    def initialize(self) -> None:
        """
        Places, rotates and initializes the torches, generates the darkness layers and activates the switching
        between them
        :return: None
        """
        self._rotate_torches()
        self.get_all_bright_areas()  # gets data of all bright tokens
        self.generate_darkness_layers()
        self.enable_darkness()

    def enable_darkness(self) -> None:
        """
        Enables the flickering of torches (if activated)
        :return: None:
        """
        if App.get_running_app().flickering_torches_on:
            self.flickering_torches = Clock.schedule_interval(lambda dt: self.darkness_flicker(dt=dt), 1 / 15)
        else:
            self.darkness_flicker(0)  # 0 is a placeholder here

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
        
    def place_torches(self, size_modifier: float) -> None:
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
                    
    def get_all_bright_areas(self, dt: float | None = None) -> None:
        """
        Stores in DungeonLayout.bright_areas one bright spot dict for each Token with bright_intensity > 0
        :param dt: delta time. Optional. This function may be scheduled
        :return: None
        """
        self.bright_areas = ([token.bright_area
                             for tile in self.dungeon.children
                             for token_list in tile.tokens.values()
                             for token in token_list if token.bright_area is not None])

        for bright_area in self.bright_areas:
            self._set_id(bright_area)

    def _set_id(self, bright_area: BrightArea) -> None:
        """
        Sets a unique id number to a BrightArea based on the id of the previous BrightArea of the list
        :return: None
        """
        if self.bright_areas.index(bright_area) == 0:
            bright_area.id = 0
        else:
            bright_area.id = self.bright_areas[self.bright_areas.index(bright_area) - 1].id + 1

    """
    def check_if_disable_flickering(self) -> bool:
        ""
        Checks if there are still flickering elements in the dungeron, if not, it casts a layer of static darkness
        :return: True if static darkness was cast, False otherwise
        ""
        if len(self.bright_areas) == 0:
            self.flickering_torches.cancel()
            # if last bright spot is removed, cast static darkness
            if self.darkness is not None: # and self.darkness.texture in self.dungeon.canvas.after.children:
                self.dungeon.canvas.after.remove(self.darkness.texture)
            self.darkness = self._create_darkness_layer()
            self.dungeon.canvas.after.add(self.darkness.texture)
            return True
        elif not self.flickering_torches.is_triggered and App.get_running_app().flickering_torches_on:
            self.flickering_torches = Clock.schedule_interval(lambda dt: self.darkness_flicker(dt=dt), 1 / 15)
        return False
    """
    
    def darkness_flicker(self, dt: float) -> None:
        """
        Wrapper function that generates a darkness with flickering brightness points. Needs to be scheduled
        using Clock.schedule_interval() and specifying the desired frequency
        :param dt: delta time
        :return: None
        """
        if self.darkness is not None:  # and self.darkness.texture in self.dungeon.canvas.after.children:
            self.dungeon.canvas.after.remove(self.darkness.texture)

        self.darkness = choice(self.darkness_layers)

        self._get_timeout_bright_areas(dt)
        # bright areas to add (if present in DarknessManager.bright_areas and not in darkness.bright_areas)
        ba_to_add: list[BrightArea] = [ba for ba in self.bright_areas if ba not in self.darkness.bright_areas]
        # bright areas to remove (if present in darkness.bright_areas and not in DarknessManager.bright_areas)
        ba_to_remove: list[BrightArea] = [ba for ba in self.darkness.bright_areas if ba not in self.bright_areas]

        for ba in ba_to_add:
            self._add_bright_area(ba)
        for ba in ba_to_remove:
            self._remove_bright_area(ba)

        self.dungeon.canvas.after.add(self.darkness.texture)

    def generate_darkness_layers(self) -> None:
        """
        Generates a number of darkness layers with different degree of flickering and stores them in a list
        :return: None
        """
        self.darkness_layers = []
        for _ in range(self.number_of_layers):
            self.darkness_layers.append(self._create_darkness_layer())

    def _create_darkness_layer(self) -> DarknessLayer:
        """
        Generates a darkness layer with optional illuminated areas
        :return: darkness layer to be displayed on the canvas
        """
        texture = Texture.create(size=self.dungeon.size, colorfmt="rgba")
        height, width = texture.height, texture.width
        flicker_mods = {}

        # unclipped alpha: pixel intensity, may go negative. Starts at darkness intensity
        pixel_int_data = np.full((height, width), self.darkness_intensity, dtype=int16)
        # 3D array. height and width: one entry per pixel of the texture.
        # 4: each pixel has four channels, red, green, blue and alpha.
        light_data = zeros((height, width, 4), dtype=uint8)
        # Sets the alpha channel of every pixel to darkness intensity
        light_data[:, :, 3] = self.darkness_intensity

        for bright_area in self.bright_areas:
            flicker_mod = uniform(*bright_area.flicker_mod_range)
            self._generate_area_data(height, width,
                                     self.darkness_intensity,
                                     bright_area,
                                     pixel_int_data,
                                     light_data,
                                     flicker_mod,
                                     revert_brightness=False)
            flicker_mods[bright_area.id] = flicker_mod

        texture.blit_buffer(light_data.ravel(), colorfmt="rgba", bufferfmt="ubyte")
        return DarknessLayer(texture=Rectangle(texture=texture, pos=self.dungeon.pos, size=self.dungeon.size),
                             pixel_int_data=pixel_int_data, light_data=light_data,
                             bright_areas=self.bright_areas[:], flicker_mods=flicker_mods)

    def _add_bright_area(self, bright_area: BrightArea) -> None:
        """
        Adds a bright area to the DarknessManager.darkness_layer
        :param bright_area: data of the bright area to add (intensity, radius, center, gradient, etc.)
        :return: None
        """
        self.darkness.bright_areas.append(bright_area)
        self._set_id(bright_area)
        self.darkness.flicker_mods[bright_area.id] = (
            uniform(bright_area.flicker_mod_range[0], bright_area.flicker_mod_range[1]))

        self._modify_darkness_layer(bright_area, revert_brightness=False)

    def _remove_bright_area(self, bright_area: BrightArea) -> None:
        """
        Removes a bright area from DarknessManager.darkness_layer
        :param bright_area: data of the bright area to remove (intensity, radius, center, gradient, etc.)
        :return: None
        """
        self._modify_darkness_layer(bright_area, revert_brightness=True)
        del self.darkness.flicker_mods[bright_area.id]
        self.darkness.bright_areas.remove(bright_area)

    def _get_timeout_bright_areas(self, dt: float) -> None:
        """
        Purges BrightArea from DarknesManager.bright_areas with exhausted duration
        :param dt: delta time
        :return: None
        """
        remaining: list[BrightArea] = []
        for ba in self.bright_areas:
            if ba.duration is not None:
                ba.elapsed_time += dt
                if ba.elapsed_time > ba.duration:
                    continue  # timeout areas are not included in remaining list
            remaining.append(ba)
        self.bright_areas = remaining

    def _modify_darkness_layer(self, bright_area: BrightArea, revert_brightness: bool) -> None:
        """
        Adds or removes a bright area from the DarknessManager.darkness, depending on the intensity value
        :param bright_area: data of the bright area (intensity, radius, center, gradient, etc)
        :param revert_brightness: bool indicating if brightness must be inverted (thus bright_area_removed)
        :return: None
        """
        height, width = self.darkness.pixel_int_data.shape

        self._generate_area_data(height, width,
                                 self.darkness_intensity,
                                 bright_area,
                                 self.darkness.pixel_int_data,
                                 self.darkness.light_data,
                                 flicker_mod=self.darkness.flicker_mods[bright_area.id],
                                 revert_brightness=revert_brightness)

        self.darkness.texture.texture.blit_buffer(self.darkness.light_data.ravel(),
                                                  colorfmt="rgba", bufferfmt="ubyte")

    @staticmethod
    def _generate_area_data(texture_height: int, texture_width: int, darkness_intensity: int, bright_area: BrightArea,
                            pixel_int_data: np.ndarray, light_data: np.ndarray, flicker_mod: float,
                            revert_brightness:bool) -> None:
        """
        Generates the pixel intensity data of an area of the darkness layer
        :param texture_height: height of the darkness texture
        :param texture_width: width of the darkness texture
        :param darkness_intensity: intensity of the darkness layer
        :param bright_area: BrightArea data to append
        :param pixel_int_data: ndarray of pixel intensity data
        :param light_data: ndarray of pixel clipped light intensity data
        :param revert_brightness: bool indicating if brightness must be inverted (thus bright_area_removed)
        :return: None
        """
        max_distance = bright_area.radius ** 2
        # 2 arrays of y and x coordinates for each pixel
        y_pos, x_pos = ogrid[:texture_height, :texture_width]

        distance_from_center = (x_pos - bright_area.center[0]) ** 2 + (y_pos - bright_area.center[1]) ** 2
        light_mask = distance_from_center < max_distance
        brightness = ((1 - (distance_from_center[light_mask] / max_distance) ** flicker_mod)
                      * darkness_intensity * bright_area.intensity).astype(int16)

        if revert_brightness:
            brightness *= -1

        pixel_int_data[light_mask] -= brightness  # raw data
        # clipped data between zero light and darkness intensity
        light_data[light_mask, 3] = clip(pixel_int_data[light_mask], 0, darkness_intensity).astype(uint8)
