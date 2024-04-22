from kivy.graphics import Ellipse, Rectangle, Color   # type: ignore
from kivy.animation import Animation
from kivy.properties import Clock
from kivy.uix.widget import Widget

import character_classes as characters
import crapgeon_utils as utils


class DamageToken(Widget):

    def __init__(self, dungeon, position, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.hit_maximmum = False
        self.fade_speed = 0.05
        self.dungeon = dungeon
        self.position = position
        self.token = None
        self.position = position
        
        Clock.schedule_interval(self.fade, 0.01)


    def fade(self, dt):

        if not self.hit_maximmum:
            self.opacity += self.fade_speed
            if self.opacity > 0.5:
                self.hit_maximmum = True

        else:
            self.opacity -= self.fade_speed
            if self.opacity < 0:
                self.canvas.clear()
                self.dungeon.game.update_switch('character_done')
                self.dungeon.get_tile(self.position).damage_token = None
                return False

        self.draw(self.opacity)


    def draw(self, opacity):
        
        with self.canvas:

            self.color = Color(1,0,0,opacity)
            self.token = Ellipse(pos = self.pos, size = self.size)
    



class SceneryToken(Rectangle):

    
    def __init__(self, position, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if wall, shovel, etc.
        self.position = position
        self.dungeon = dungeon_instance
        self.source = self.kind + 'token.png'


class CharacterToken(Ellipse):

    
    def __init__(self, position, kind, species, dungeon_instance, character, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if monster, player, wall, etc.
        self.species = species
        self.position = position
        self.dungeon = dungeon_instance
        self.character = character      #links token with character object
        self.source = self.species + 'token.png'
        self.start = None   #all defined when token is moved by move()
        self.goal = None    
        self.path = None


    def move_player (self, start_tile, end_tile):

        if start_tile == end_tile:     #if character stays in place
            
            self.dungeon.game.next_character()
        
        else:
        
            self.start = start_tile

            self.goal = end_tile
            
            self.path = self.dungeon.find_shortest_path(self.start, self.goal, (self.character.blocked_by))

            self.dungeon.activate_which_tiles()     #tiles desactivated while moving
            
            self.slide(self.path)
                    
    
    def move_monster(self):

        self.start = self.dungeon.get_tile(self.position)

        self.path = self.character.move()

        self.goal = self.dungeon.get_tile(self.path[-1])

        self.slide(self.path)


    def slide (self, path):

            
        next_position = path.pop(0)

        next_pos = self.dungeon.get_tile(next_position).pos
        
        self.character.remaining_moves -= 1
        
        animation = Animation (pos = next_pos, duration = 0.2)
        
        animation.bind (on_complete = self.on_slide_completed)
        
        animation.start(self)


    def on_slide_completed (self, *args):

        if len(self.path) > 0:

            self.slide(self.path)

        else:   #if goal is reached
            
            if isinstance(self.character, characters.Player):    
            
                if self.goal.kind == 'exit':

                    self.dungeon.game.dungeon_finished = True
                    
                elif self.goal.has_token('shovel') or self.goal.has_token('weapon'):

                    self.character.pick_object(self.goal.token.kind)

                    self.goal.clear_token()

            
            if self.start != self.goal:
                
                self.update_on_tiles(self.start, self.goal) #updates tile.token
                
                self.character.update_position(self.goal.row, self.goal.col)

            
            if isinstance(self.character, characters.Monster) and self.character.remaining_moves > 0:
                
                for player in characters.Player.data:

                    if utils.are_nearby(self.character, player):

                        self.character.attack(player)

                    else:
                        self.dungeon.game.update_switch('character_done')

            else:
                self.dungeon.game.update_switch('character_done')

            


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
                
                characters.Player.data.remove(self.goal.token.character)

                self.goal.token.character.rearrange_ids()

                self.dungeon.canvas.remove(self.goal.token)

                self.goal.token = None

                return True 

            else:

                return False