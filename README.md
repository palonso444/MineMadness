Description of the branch
---------------------------

This branch contains the beginning of the implementation of dynamite explosion affecting multiple Tiles.

Requires to improve the system of throwing dynamite (more range, not enough if there is connexion. A system of realistic vision field must be implemented)

Implement a counter of dodging tokens. Substract one at the end of on_dodge_completed. When it reaches 0, make dynamite explode in Tile stored as attribute of DungeonLayout
