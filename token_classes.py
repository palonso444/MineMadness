from kivy.graphics import Ellipse, Rectangle, Color   # type: ignore
from kivy.animation import Animation
#from kivy.properties import Clock, BooleanProperty
from kivy.uix.widget import Widget

import character_classes as characters
import crapgeon_utils as utils


class FadingToken(Widget):

    def __init__(self, dungeon, **kwargs):
        super().__init__(**kwargs)
        self.opacity = 0
        self.final_opacity = None
        self.dungeon = dungeon

            
    def fade(self):

        def fade_out(*args):

            fading = Animation(opacity=0, duration=0.2)
            fading.start(self)

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
        
        self.fade()


class DiggingToken(FadingToken):

    def __init__(self, dungeon, **kwargs):
        super().__init__(dungeon,**kwargs)
        self.final_opacity = 0.7

        with self.canvas:

            self.color = Color(0.58,0.294,0,1)
            self.token = Rectangle(pos = self.pos, size = self.size)
        
        self.fade()


class SceneryToken(Rectangle):

    
    def __init__(self, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if wall, shovel, etc.
        self.dungeon = dungeon_instance
        self.source = self.kind + 'token.png'


class CharacterToken(Ellipse):

    
    def __init__(self, kind, species, dungeon_instance, character, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if monster, player, wall, etc.
        self.species = species
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

        self.start = self.dungeon.get_tile(self.character.position)

        self.path = self.character.move()

        if self.path is None:  # if cannot move, will try directly to attack players
            self.character.attack_players()
            self.dungeon.game.update_switch('character_done')

        else:
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
            
                if self.goal.kind == 'exit' and characters.Player.gems == self.dungeon.game.total_gems:

                    self.update_on_tiles(self.start, self.goal) #updates tile.token
                    self.character.update_position(self.goal.row, self.goal.col)
                    self.dungeon.game.update_switch('player_exited')
                    return
                    
                elif self.goal.has_token('shovel') or self.goal.has_token('weapon') or self.goal.has_token('gem'):

                    self.character.pick_object(self.goal)

            
            if self.start != self.goal:
                
                self.update_on_tiles(self.start, self.goal) #updates tile.token
                self.character.update_position(self.goal.row, self.goal.col)

            
            if isinstance(self.character, characters.Monster):

                self.character.attack_players()

            
            self.dungeon.game.update_switch('character_done')


    def update_on_tiles(self, start_tile, end_tile):

        if end_tile.token and end_tile.token.kind in self.character.ignores:
            end_tile.second_token = self
        else:
            end_tile.token = self

        if start_tile.second_token:
            start_tile.second_token = None
        else:
            start_tile.token = None