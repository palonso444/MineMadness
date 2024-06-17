ISSUES FOR THIS GAME
--------------------

ONGOING WORK: implement ability buttons. Disable button on main.py when adjusting button state by calling on_activity_button()
              implement experience when killing monsters and leveling up
              implement overdosing when abusing of powerups

Monster idea: a Monster with high number of moves and low health that attacks player and goes away so it's hard to kill. Make this feature a monster attribute 

Make character tokens become more and more red when heath goes lower and lower. monsters and players 

Mark selected player

Move all logic of on_complete (token_slide) from token classes to main.

Right now, when the level is over, generate_next_level() (within the App class) resets the whole CrapgeonGame widget, when only reseting the dungeon is necessary. Fix. Generate new level as method of dungeon layout. Així es podrà eliminar només aquest widget, no tota la interface. Generate blueprint must be on_level of CrapgeonGame. Level is CrapgeonGame attribute, by starting only the dungeon at each level, this attribute will not be reset. Make sure that game works if players exit level in one turn without monster turn (if turn.counter does not change from 0 to 1 it may cause bug). Also make sure counter is reset to 0 at start new level.

Character progression. Each monster give experience. At some point you can level up and increase movement, strength, digging ability. Change character attributes from tuple to lists so they can be modified.

Hawkins and Crusher Jane can die and game continues. With some items found in later levels is possible to revive characters. If Sawyer dies game is over. Item to revive character has 2 uses: revive and, if used on a live character, enhance permanently its movement and strength by 1

Print level number on screen

Movement not smooth like now but more like steps

Green token when something good happens to player

BUG: sometimes players appear semitransparent when movement range is showed 

BUG: wisps pass sometimes above the walls. Should pass always under them

Sawyer té opció hidden, crusher jane armed and unarmed i hawkins a part dexcavar també pot fer volar la cova per bloquejar caselles (fa aparèixer una paret). Si la casella té monstre, el monstre reb a saco de mal i passa a second token si sobreviu. Si hi ha armes o pales es perden i alliberen el tile.token per la wall i monstre passa al second token.

Sawyer can hide after picking an object that she only can pick. This enabled her ability to hide. When hidden, monsters cannot attack her but she cannot attack or pick any object 

Search tiles yield a random object (good one, whisky, tobacco or talisman) but cost one move to search and a monster may also appear. Above-mentioned object rarely appear out of search tiles.

Hawkin can pick shovels. He is the only one that can dig diamond walls, consuming shovels as normal characters do

Reset character order at the beginning of each turn so it begins always sawyer, hawkins cruser Jane. Define this order as tuple in game stats file

If there are no monsters players can be activated even if they have moved 

Dungeon should not grow so fast


IDEAS FOR SECOND PART
-----------------------

Include range weapons

Monster can pick objects. Kill monster and object is dropped on its spot.

Invisible traps triggered if player goes to trap spot

Characters monsters and players have self.hidden property and can hide. Self.armed to check if they use weapons.

Players heal a bit when they change floor

Use instance, value instead of *args in on_event callbacks where value is used (on_turn, on_inv_object, etc.)

Make tobacco token as an old can of chewing tobacco.
