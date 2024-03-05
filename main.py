from kivy.app import App    # type: ignore
from kivy.uix.boxlayout import BoxLayout    # type: ignore
from kivy.uix.gridlayout import GridLayout    # type: ignore
#from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.label import Label    # type: ignore
from kivy.uix.button import Button  # type: ignore
#from kivy.core.text import LabelBase    # type: ignore
#from kivy.uix.image import Image    # type: ignore
from kivy.graphics import Ellipse

import crapgeon_utils as utils
import crapgeon_classes as classes
import copy


#LabelBase.register(name = 'Vollkorn',
                   #fn_regular= 'fonts/Vollkorn-Regular.ttf',
                   #fn_italic='fonts/Vollkorn-Italic.ttf'



class Token(Ellipse):   #Tokens have id that identifies them (as Monsters or Player)

    def __init__(self, kind, id, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if monster, player, wall, etc.
        self.id = id        #defines index in monsters or players lists



class DungeonTile(Button):

    #row = ObjectProperty(0)
    #col = NumericProperty(0)
    
    def __init__(self, row, col, **kwargs):
        super().__init__(**kwargs)

        self.row = row
        self.col = col
        self.token = None   #defined later when token is placed on tile by DungeonLayout.place_tokens

    
    #def on_release (self, token, end_row, end_col):

        #DungeonLayout.move_token((self.token, self.row, self.col))

    
    def bind_token (self, *args):  #function called within DungeonLayout.place_tokens

        self.token.pos = self.pos
        self.token.size = self.size



class DungeonLayout(GridLayout):
    
    
    def __init__(self, height, width, **kwargs):
        super().__init__(**kwargs)
        
        self.blueprint = self.generate_blueprint(height, width)
        self.rows = height
        self.cols = width

        for y in range (self.rows):
              
            for x in range (self.cols):
                
                tile = DungeonTile(row=y, col=x) #text = self.blueprint[y][x]
                
                self.add_widget(tile)


    def generate_blueprint (self, height, width):

        dungeon_blueprint = utils.create_map(height, width)

        utils.place_single_items(dungeon_blueprint,'%', 1, (9,5))
        utils.place_single_items(dungeon_blueprint,'o', 5)
        utils.place_single_items(dungeon_blueprint,' ', 1)

        for key,value in {'M': 0, '#': 0.6, 'p': 0.05, 'x': 0.05, 's': 0.02}.items():  #.items() method to iterate over key and values, not only dkeys (default)
        
            utils.place_items (dungeon_blueprint, item=key, frequency=value)

        return dungeon_blueprint
    

    def place_tokens (self):

        for tile in self.children:

            if self.blueprint [tile.row][tile.col] in classes.Character.blueprint_ids:
        
                with self.canvas:

                    if self.blueprint [tile.row][tile.col] == '%':

                        tile.token = Token(source = 'playertoken.png', kind = 'player', id = len(classes.Player.players))
                        player = classes.Player (position = (tile.row, tile.col), moves = 4)    #create player object
                        classes.Player.players.append (player)  #add player to players list

                    elif self.blueprint [tile.row][tile.col] == 'M':

                        tile.token = Token(source = 'monstertoken.png', kind = 'monster', id = len(classes.Monster.monsters))
                        monster = classes.Monster(position = (tile.row, tile.col), moves = 1)   #create monster object
                        classes.Monster.monsters.append (monster)   #create monster to monsters list
                    
                    tile.bind (pos = tile.bind_token, size = tile.bind_token)



    def activate_tiles(self, tile_positions):

        for tile in self.children:

            for position in tile_positions:

                if tile.row == position[0] and tile.col == position[1]:

                    tile.disabled = False

    
    
    
    def move_token(self, end_tile):

        
        for player in classes.Player.players:

            for tile in self.children:

                if tile.token is not None and tile.token.id == classes.Player.players.index(player):

                    tile.token.pos = end_tile.pos
                    #end_tile.token = tile.token
                    #del tile.token
                    #tile.token = None

                    #tile.token = None
                    #break

                    print (tile.token)
                    print (end_tile.token)



                    #end_tile.token = tile.token
                    #end_tile.bind (pos = end_tile.bind_token, size = end_tile.bind_token)
                    #tile.token = None



class CrapgeonApp(App):

    def build (self):

        main_layout = BoxLayout()

        self.dungeon = DungeonLayout(10,10) #dungeon is attribute of app so move_token() can be called from kv file.

        self.dungeon.place_tokens()
        
        main_layout.add_widget(self.dungeon)

        movement_range = classes.Player.players[0].get_movement_range(self.dungeon)

        self.dungeon.activate_tiles(movement_range)

        return main_layout
    
    #def update_movement():

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()