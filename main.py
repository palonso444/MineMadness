from kivy.app import App    # type: ignore
from kivy.uix.boxlayout import BoxLayout    # type: ignore
from kivy.uix.gridlayout import GridLayout    # type: ignore
#from kivy.uix.scrollview import ScrollView  # type: ignore
#from kivy.uix.label import Label    # type: ignore
from kivy.uix.button import Button  # type: ignore
#from kivy.core.text import LabelBase    # type: ignore
#from kivy.uix.image import Image    # type: ignore
#from kivy.graphics import Ellipse, Rectangle   # type: ignore
#from kivy.uix.widget import Widget  # type: ignore
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, StringProperty, Clock   # type: ignore
#from kivy.animation import Animation


import crapgeon_utils as utils
import character_classes as characters
import token_classes as tokens
import dungeon_classes as dungeons
import tile_classes as tiles
from collections import deque


#LabelBase.register(name = 'Vollkorn',
                   #fn_regular= 'fonts/Vollkorn-Regular.ttf',
                   #fn_italic='fonts/Vollkorn-Italic.ttf'



class CrapgeonGame(BoxLayout):  #initlialized in kv file
    
    
    active_character_id = NumericProperty(0)

    dungeon = ObjectProperty(None)

    dungeon_finished = BooleanProperty(False)
 
    turn = BooleanProperty(None)        #Those are switches to trigger change of turn and updating of info labels
    health = BooleanProperty(None)      #defined in kv file upon changes in player properties
    shovels = BooleanProperty(None)
    weapons = BooleanProperty(None)
    gems = BooleanProperty(None)

    #self.active_character is initialized and defined within on_active_character_id()
    
    
    def initialize_switches(self):

        self.turn = True    #TRUE for players, FALSE for monsters. Player starts

        self.health = False
        self.shovels = False
        self.weapons = False
        self.gems = False
    
    
    def on_dungeon(self, *args):

        
        self.dungeon.allocate_tokens()
        self.initialize_switches()

    
    def next_character(self):

        
        if self.active_character.id == len(self.active_character.__class__.data) - 1: #if all players or monsters have moved
            
            self.turn = not self.turn   #turn changes

        
        else: 
            
            self.active_character_id += 1       # next character on list moves


    def on_turn (self, *args):
        
        
        if self.active_character_id != 0:
                
            self.active_character_id = 0

        else:

            self.on_active_character_id ()  #must be called manually if self.active_character_id does not change

    
    def dynamic_movement_range(self):

        
        movement_range = self.active_character.get_movement_range(self.dungeon)

        self.dungeon.activate_which_tiles(movement_range)


    def on_active_character_id (self, *args):

        
        if self.turn or len(characters.Monster.data) == 0:   #if player turn or no monsters (always players turn)

            self.active_character = characters.Player.data[self.active_character_id]
            
            self.active_character.remaining_moves = self.active_character.moves

            self.dynamic_movement_range()

        
        elif not self.turn:  #if monsters turn and monsters in the game

            self.dungeon.activate_which_tiles() #tiles deactivated in monster turn
            
            self.active_character = characters.Monster.data[self.active_character_id]
                
            self.active_character.token.move_monster()


    def on_dungeon_finished(self, *args):

        print ('DUNGEON FINISHED!')


class CrapgeonApp(App):

    def build (self):

        return CrapgeonGame()

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()