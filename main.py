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



def generate_template (height, width):

    dungeon_template = utils.create_map(height, width)

    utils.place_single_items(dungeon_template,'%', 1, (0,0))
    utils.place_single_items(dungeon_template,'o', 5)
    utils.place_single_items(dungeon_template,' ', 1)

    for key,value in {'M': 0.1, '#': 0.6, 'p': 0.05, 'x': 0.05, 's': 0.02}.items():  #.items() method to iterate over key and values, not only dkeys (default)
        
        utils.place_items (dungeon_template, item=key, frequency=value)



    return dungeon_template



class DungeonLayout(GridLayout):
    
    
    def __init__(self, template, **kwargs):
        super().__init__(**kwargs)
        
        self.rows = len(template)
        self.cols = len(template[0])

        for y in range (self.rows):
              
            for x in range (self.cols):
                
                tile = Button(text= template[y][x])
                
                self.add_widget(tile)



class CrapgeonApp(App):

    def build (self):

        main_layout = BoxLayout()
        
        template = generate_template(10,10)

        dungeon = DungeonLayout(template)
        
        main_layout.add_widget(dungeon)

        return main_layout

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()