Description of current code
---------------------------

This is a complete beta-version mechanic-wise but it is not properly balanced or debugged.
See the attached README_debugging file for what needs to be done regarding debugging. There is no guarantee that mechanics function well!!
More monsters must be created (special ones).
Only rock walls are in this version. Granite or Quarz walls are implemented but need to be included in the
game_progression() function of game.stats.py

Ideas for upcoming versions
---------------------------

Monster can pick objects. Kill monster and object is dropped on its spot.

Invisible traps triggered if player goes to trap spot

Characters monsters and players have self.hidden property and can hide. Self.armed to check if they use weapons.

Implement overdosing

Monster idea: a Monster with high number of moves and low health that attacks player and goes away so it's hard to kill. Make this feature a monster attribute

Crusher jane may have digging as free action when reaching high levels.

Path smart they go to the nearest player even if they cannot reach it because is surrounded by monsters. In this case, they should go after another player if they can reach it.

Search tiles yield a random object (good one, whisky, tobacco or talisman) but cost one move to search and a monster may also appear. The above-mentioned object rarely appear out of search tiles.

Save the game at the beginning of each level. Game is deleted if killed(hard mode) or not (smooth mode). To save the game, take a snapshot of the position of each token and store it in a dictionary to be able to reconstruct the board. Consider updating token.pos when slide finishes (right now only token.position is updated) and reconstruct the board with pos (may be more efficient)

Unbind button at beginning of on_ability_button and bind it again at the end

Pass max number of steps to dynamic movement range and tile.is_activable so range can be set dynamically and does not depend on players attributes 

BUG: sometimes players appear semitransparent when movement range is showed 

BUG: wisps pass sometimes above the walls. Should pass always under them

BUG: characters don't level up

Level number as a popup at beginning of level

Player can assign points to character when leveling up

Hawkins and Crusher Jane can die and game continues. If Sawyer dies game is over.

Use animation transitions property (see documentation) to make sliding not be uniform but resemble steps

Hawkins gains experience when blowing with dynamite monsters with high dodging_ability 

Monsters that stay on gems make no sense, they should leave the gems, attack player, go back to gem

Monster idea: Giant Earthgrub, chases player and goes accross rock walls by eating them

Pixie: right now it takes gems, but this should be like that for future versions. Pixie should take pickables except for gems (it breaks the game). Write a pick_object() method for monsters. Consider including monster inventory.

Consider including more kinds of tiles to give visual variety to the levels
