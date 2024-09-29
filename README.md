Description of current code
---------------------------

This is a complete beta-version mechanic-wise but it is not properly balanced or debugged.
See the attached README_debugging file for what needs to be done regarding debugging. There is no guarantee that mechanics function well!!
print statements of the code must be removed after debugging
More monsters must be created (special ones).
Only rock walls are in this version. Granite or Quarz walls are implemented but need to be included in the
game_progression() function of game.stats.py

Ideas for upcoming versions
---------------------------

Characters monsters and players have self.hidden property and can hide. Self.armed to check if they use weapons.

Monster idea: a Monster with high number of moves and low health that attacks player and goes away so it's hard to kill. Make this feature a monster attribute

Crusher jane may have digging as free action when reaching high levels.

Search tiles yield a random object (good one, whisky, tobacco or talisman) but cost one move to search and a monster may also appear. The above-mentioned object rarely appear out of search tiles.

Pass max number of steps to dynamic movement range and tile.is_activable so range can be set dynamically and does not depend on players attributes 

Monsters that stay on gems make no sense, they should leave the gems, attack player, go back to gem
