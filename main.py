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

#LabelBase.register(name = 'Vollkorn',
                   #fn_regular= 'fonts/Vollkorn-Regular.ttf',
                   #fn_italic='fonts/Vollkorn-Italic.ttf'



class Token(Ellipse):   #Tokens have id that identifies them (as Monsters or Player)

    def __init__(self, id, **kwargs):
        super().__init__(**kwargs)

        self.id = id



class DungeonTile(Button):
    def __init__(self, item, pos_y, pos_x, **kwargs):
        super().__init__(**kwargs)

        self.item = item
        self.pos_y = pos_y
        self.pos_x = pos_x
        self.token = None   #defined later when token is placed on tile by DungeonLayout.place_tokens

    
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
                
                tile = DungeonTile(text= self.blueprint[y][x], item = self.blueprint[y][x], pos_y=y, pos_x=x)
                
                self.add_widget(tile)


    def generate_blueprint (self, height, width):

        dungeon_blueprint = utils.create_map(height, width)

        utils.place_single_items(dungeon_blueprint,'%', 1, (0,0))
        utils.place_single_items(dungeon_blueprint,'o', 5)
        utils.place_single_items(dungeon_blueprint,' ', 1)

        for key,value in {'M': 0.2, '#': 0.6, 'p': 0.05, 'x': 0.05, 's': 0.02}.items():  #.items() method to iterate over key and values, not only dkeys (default)
        
            utils.place_items (dungeon_blueprint, item=key, frequency=value)

        return dungeon_blueprint
    

    def place_tokens (self):

        for tile in self.children:

            if tile.item in classes.Character.blueprint_ids:
        
                with self.canvas:

                    if tile.item == '%':

                        tile.token = Token(id = tile.item, source = 'playertoken.png')

                    elif tile.item == 'M':

                        tile.token = Token(id = tile.item, source = 'monstertoken.png')
                    
                    tile.bind (pos = tile.bind_token, size = tile.bind_token)



class CrapgeonApp(App):

    def build (self):

        main_layout = BoxLayout()

        dungeon = DungeonLayout(10,10)

        dungeon.place_tokens()
        
        main_layout.add_widget(dungeon)

        return main_layout

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()