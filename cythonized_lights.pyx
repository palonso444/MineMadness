from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture
from random import choice, uniform
from numpy cimport ndarray, uint8_t, int16_t
from numpy import uint8, int16, clip, ogrid, zeros

cpdef object generate_darkness_layer(object dungeon, int alpha_intensity):
    """
    Generates a darkness layer with optional illuminated areas
    :param alpha_intensity: alpha intensity of the darkness. Must range from 0 to 255
    :return: darkness layer to be displayed on the canvas
    """
    cdef:
        object texture
        ndarray[uint8_t, ndim=3] data
        dict bright_spot
        float gradient, max_distance
        ndarray y_pos, x_pos
        ndarray distance_from_center
        ndarray light_mask
        ndarray brightness
        ndarray[int16_t, ndim=1] temp_data

    texture = Texture.create(size=dungeon.size, colorfmt="rgba")
    data = zeros((texture.height, texture.width, 4), dtype=uint8)
    data[:, :, 3] = alpha_intensity

    for bright_spot in dungeon.bright_spots:
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

    return Rectangle(texture=texture, pos=dungeon.pos, size=dungeon.size)