from kivy.graphics import Ellipse, Rectangle, Color   # type: ignore
from kivy.animation import Animation
from kivy.properties import Clock, BooleanProperty
from kivy.uix.widget import Widget

import character_classes as characters
import crapgeon_utils as utils


class FadingToken(Widget):

    def __init__(self, dungeon, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.final_opacity = None
        self.dungeon = dungeon

    '''def fade(self, dt):

        if not self.hit_maximmum:
            self.opacity += self.fade_speed
            if self.opacity > 0.4:
                self.hit_maximmum = True

        else:
            self.opacity -= self.fade_speed
            if self.opacity < 0:
                self.dungeon.game.update_switch('character_done')
                return False'''
            
    def fade(self):

        def fade_out(*args):

            fading = Animation(opacity=0, duration=0.2)
            #fading.bind (on_complete = end_event)
            fading.start(self)

        #def end_event(*args):
            #pass

            #self.dungeon.game.update_switch('character_done')

        fading = Animation(opacity=self.final_opacity, duration=0.2)
        fading.bind (on_complete = fade_out)
        fading.start(self)


class DamageToken(FadingToken):

    def __init__(self, dungeon, **kwargs):
        super().__init__(dungeon,**kwargs)
        self.final_opacity = 0.4

        with self.canvas:

            self.color = Color(1,0,0,1)
            self.token = Ellipse(pos = self.pos, size = self.size)
        
        #Clock.schedule_interval(self.fade, 1/60)
        self.fade()


class DiggingToken(FadingToken):

    def __init__(self, dungeon, **kwargs):
        super().__init__(dungeon,**kwargs)
        self.final_opacity = 0.7

        with self.canvas:

            self.color = Color(0.58,0.294,0,1)
            self.token = Rectangle(pos = self.pos, size = self.size)
        
        #Clock.schedule_interval(self.fade, 1/60)
        self.fade()


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
            
            self.character.remaining_moves = 0
            self.dungeon.game.update_switch('character_done')
        
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

                    self.dungeon.game.update_switch('dungeon_finished')
                    
                elif self.goal.has_token('shovel') or self.goal.has_token('weapon') or self.goal.has_token('gem'):

                    print (self.goal.token)
                    self.character.pick_object(self.goal)


            
            if self.start != self.goal:
                
                self.update_on_tiles(self.start, self.goal) #updates tile.token
                
                self.character.update_position(self.goal.row, self.goal.col)

            
            if isinstance(self.character, characters.Monster) and self.character.remaining_moves > 0:
                
                for player in characters.Player.data:

                    if utils.are_nearby(self.character, player):

                        player_tile = self.dungeon.get_tile(player.position)

                        print (player_tile)
                        
                        self.character.fight_on_tile(player_tile)

                    #else:
                        #self.dungeon.game.update_switch('character_done')

            #else:
            self.dungeon.game.update_switch('character_done')

            


    def update_on_tiles(self, start_tile, end_tile):

        if end_tile.token and end_tile.token.kind in self.character.ignores:
            end_tile.monster_token = self
        else:
            end_tile.token = self

        if start_tile.monster_token:
            start_tile.monster_token = None
        else:
            start_tile.token = None