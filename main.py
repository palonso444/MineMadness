from kivy.app import App    # type: ignore
from kivy.uix.boxlayout import BoxLayout    # type: ignore
from kivy.uix.gridlayout import GridLayout    # type: ignore
#from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.label import Label    # type: ignore
from kivy.uix.button import Button  # type: ignore
#from kivy.core.text import LabelBase    # type: ignore
#from kivy.uix.image import Image    # type: ignore


#LabelBase.register(name = 'Vollkorn',
                   #fn_regular= 'fonts/Vollkorn-Regular.ttf',
                   #fn_italic='fonts/Vollkorn-Italic.ttf'


class DungeonFloor(GridLayout):
    
    def __init__(self, x_axis = 10, y_axis = 10, **kwargs):
        super().__init__(**kwargs)
        self.rows = y_axis
        self.cols = x_axis
        self.tiles = y_axis * x_axis

        for tile in range(self.tiles):

            tile = Button()
            self.add_widget(tile)



class CrapgeonApp(App):

    pass


    #def build (self):

        #dungeon = DungeonFloor()

        #layout = BoxLayout()
        
        #layout.add_widget(dungeon)

        #return layout

        #return BoxLayout()

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()