from kivy.app import App    # type: ignore
from kivy.uix.boxlayout import BoxLayout    # type: ignore
from kivy.uix.gridlayout import GridLayout    # type: ignore
#from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.label import Label    # type: ignore
from kivy.uix.button import Button  # type: ignore
#from kivy.core.text import LabelBase    # type: ignore
#from kivy.uix.image import Image    # type: ignore

import crapgeon_utils as utils

#LabelBase.register(name = 'Vollkorn',
                   #fn_regular= 'fonts/Vollkorn-Regular.ttf',
                   #fn_italic='fonts/Vollkorn-Italic.ttf'


class DungeonTile(Button):
    def __init__(self, item, pos_y, pos_x, **kwargs):
        super().__init__(**kwargs)

        self.item = item
        self.pos_y = pos_y
        self.pos_x = pos_x


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

        for key,value in {'M': 0.1, '#': 0.6, 'p': 0.05, 'x': 0.05, 's': 0.02}.items():  #.items() method to iterate over key and values, not only dkeys (default)
        
            utils.place_items (dungeon_blueprint, item=key, frequency=value)

        return dungeon_blueprint



class CrapgeonApp(App):

    def build (self):

        main_layout = BoxLayout()

        dungeon = DungeonLayout(10,10)
        
        main_layout.add_widget(dungeon)

        return main_layout

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()