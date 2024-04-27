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
    
    
    active_character_id = NumericProperty(None, allownone = True)

    dungeon = ObjectProperty(None)

    dungeon_finished = BooleanProperty(False)
    character_done = BooleanProperty(False)
    
    turn = BooleanProperty(None)
            #Those are switches to trigger change of turn and updating of info labels
    health = BooleanProperty(None)      #defined in kv file upon changes in player properties
    shovels = BooleanProperty(None)
    weapons = BooleanProperty(None)
    gems = BooleanProperty(None)

    #self.active_character is initialized and defined within on_active_character_id()
    #self.total_gems is initialized within DungeonLayout on_pos()
    
    
    def initialize_switches(self):

        self.turn = True    #TRUE for players, FALSE for monsters. Player starts
                            #on_turn initializes active_character_id

        self.health = False
        self.shovels = False
        self.weapons = False
        self.gems = False
    

    def update_switch(self, switch_name):

        switch_value = getattr(self, switch_name)
        switch_value = not switch_value
        setattr(self, switch_name, switch_value)
        
    
    def on_dungeon(self, *args):

        
        self.dungeon.allocate_tokens()
        self.initialize_switches()

    
    def on_character_done(self, *args):

        if isinstance(self.active_character, characters.Player) and self.active_character.remaining_moves > 0:
                
            self.dynamic_movement_range()    #checks if player can still move

        else:
            
            self.next_character() #switch turns if character last of character.characters


    def on_turn (self, *args):
        
        if self.turn or len(characters.Monster.data) == 0:
            characters.Player.reset_moves()
        else:
            characters.Monster.reset_moves()
        
        if self.active_character_id == 0:
            self.active_character_id = None
                
        self.active_character_id = 0


    def on_active_character_id (self, *args):

        
        if self.active_character_id is not None:
        
            if self.turn or len(characters.Monster.data) == 0:   #if player turn or no monsters (always players turn)

                self.active_character = characters.Player.data[self.active_character_id]

                if self.active_character.has_moved():
                    self.next_character()
            
                else:
                    self.update_switch('health')    #must be updated here after seting player as active character
                    self.dynamic_movement_range()

        
            elif not self.turn:  #if monsters turn and monsters in the game

                self.dungeon.activate_which_tiles() #tiles deactivated in monster turn
            
                self.active_character = characters.Monster.data[self.active_character_id]
                
                self.active_character.token.move_monster()


    def on_dungeon_finished(self, *args):

        if self.active_character.gems == self.total_gems:

            print ('DUNGEON FINISHED!!!')


    def next_character(self):

        if self.active_character.id < len(self.active_character.__class__.data) - 1:

            self.active_character_id += 1       # next character on list moves

        else:   #if end of characters list reached (all have moved)
            
            self.update_switch('turn')

    
    def dynamic_movement_range(self):

        
        players_not_yet_active = set()

        for player in characters.Player.data:

            if not player.has_moved():

                players_not_yet_active.add(player.position)
    
        player_movement_range = self.active_character.get_movement_range(self.dungeon)

        positions_in_range = players_not_yet_active.union(player_movement_range)
        
        self.dungeon.activate_which_tiles(positions_in_range)
        

    def switch_character(self, new_active_character):
        
        if self.active_character.has_moved():
            self.active_character.remaining_moves = 0
        
        index_new_char = characters.Player.data.index(new_active_character)
        index_old_char = characters.Player.data.index(self.active_character)
        characters.Player.data[index_old_char], characters.Player.data[index_new_char] = characters.Player.data[index_new_char], characters.Player.data[index_old_char]
        
        self.active_character.rearrange_ids()

        self.active_character = new_active_character
        
        self.active_character_id = None
        self.active_character_id = characters.Player.data.index(self.active_character)


class CrapgeonApp(App):

    def build (self):

        return CrapgeonGame()

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()