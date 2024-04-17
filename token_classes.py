from kivy.graphics import Ellipse, Rectangle   # type: ignore
from kivy.animation import Animation

import character_classes as characters


class SceneryToken(Rectangle):

    
    def __init__(self, position, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if wall, shovel, etc.
        self.position = position
        self.dungeon = dungeon_instance


class CharacterToken(Ellipse):

    
    def __init__(self, position, kind, species, dungeon_instance, character, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if monster, player, wall, etc.
        self.species = species
        self.position = position
        self.dungeon = dungeon_instance
        self.character = character      #links token with character object
        
        self.start = None   #all defined when token is moved by move()
        self.goal = None    
        self.path = None    


    def move_player (self, start_tile, end_tile):

        
        if start_tile == end_tile:     #if character stays in place
            
            self.dungeon.game.next_character()
        
        else:
        
            self.start = start_tile

            self.goal = end_tile
            
            self.path = self.dungeon.find_shortest_path(self.start, self.goal, ('wall', 'monster'))

            self.dungeon.activate_which_tiles()     #tiles desactivated while moving
            
            self.slide(self.path)
                    
    
    def move_monster(self):

        self.start = self.dungeon.get_tile(self.position)

        self.path = self.character.assess_path_direct()
        self.goal = self.dungeon.get_tile(self.path[-1])

        self.slide(self.path)


    def slide (self, path):

            
        next_position = path.pop(0)

        next_pos = self.dungeon.get_tile(next_position).pos

        if isinstance(self.character, characters.Player):  #monsters always complete movement.
        
            self.character.remaining_moves -= 1
        
        animation = Animation (pos = next_pos, duration = 0.3)
        
        animation.bind (on_complete = self.on_slide_completed)
        
        animation.start(self)


    def on_slide_completed (self, *args):


        if len(self.path) == 0:     #if goal is reached
            
            if self.goal.kind == 'exit' and self.token.kind == 'player':

                self.dungeon.game.dungeon_finished = True
            
            else:

                if isinstance(self.character, characters.Player):  #weapons and shovels. Monsters and walls resolved within before moving, within on_release()
                    
                    if self.goal.monster_token or self.goal.token:

                        self.goal.clear_token(self.character)
                
                self.update_on_tiles(self.start, self.goal) #updates tile.token of start and goal
                
                self.character.update_position(self.goal.row, self.goal.col)

                if isinstance(self.character, characters.Player) and self.character.remaining_moves > 0:
                    
                    self.dungeon.game.dynamic_movement_range()    #checks if player can still move

                else:
            
                    self.dungeon.game.next_character() #switch turns if character last of character.characters
        
        
        else:   # if len(path) > 0, goal is not reached, continue sliding

            self.slide(self.path)


    def update_on_tiles(self, start_tile, end_tile):


        #IF END_TILE OCCUPIED, MONSTERTOKEN IS STORED TO SPECIAL TOKEN SLOT
        if end_tile.token and isinstance(self.character, characters.Monster):
            end_tile.monster_token = self
        else:

            end_tile.token = self

        # IF SECONDARY SLOT OCCUPIED IN START TILE, IT IS SET TO NONE. MAIN SLOT REMAINS UNTOUCHED
        if start_tile.monster_token:

            start_tile.monster_token = None
        
        else:

            start_tile.token = None

    
    def manage_collision(self):     #DEPRECATED! CODE USED IN clear_token()

        #if self.kind == 'player':

            #if self.goal.token.kind == 'monster':

                #self.goal.token.character.rearrange_ids()

                #classes.Monster.data.remove(self.goal.token.character)

                #print ('REMAINING MONSTERS')
                #print (len(classes.Monster.data))
                
                #print ('REMAINING MONSTER IDS')
                #for monster in classes.Monster.data:
                    #print (monster.id)

                #self.dungeon.canvas.remove(self.goal.token)

                #self.goal.token = None

                #return True

            #else:

                #return False

        if self.kind == 'monster':

            if self.goal.token.kind == 'player':

                self.goal.token.character.rearrange_ids()
                
                characters.Player.data.remove(self.goal.token.character)

                self.dungeon.canvas.remove(self.goal.token)

                self.goal.token = None

                return True 

            else:

                return False