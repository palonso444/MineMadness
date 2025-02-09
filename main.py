from os import path
import sys

from kivy.app import App    # type: ignore
from kivy.uix.boxlayout import BoxLayout    # type: ignore
from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.label import Label    # type: ignore
from kivy.uix.button import Button  # type: ignore
from kivy.core.text import LabelBase    # type: ignore
from kivy.uix.image import Image    # type: ignore

import autorol_utils    # type: ignore

# this is needed to set the correct path to resources when compiling with Pyinstaller
def get_resource_path(relative_path):

    if getattr(sys, 'frozen', True) and hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = path.abspath(".")

    return path.join(base_path, relative_path)

LabelBase.register(name = 'Vollkorn',
                   fn_regular= get_resource_path('fonts/Vollkorn-Regular.ttf'),
                   fn_italic=get_resource_path('fonts/Vollkorn-Italic.ttf'))

LabelBase.register(name = 'CreteRound',
                   fn_regular= get_resource_path('fonts/CreteRound-Regular.ttf'))

LabelBase.register(name = 'Chiller',
                   fn_regular= get_resource_path('fonts/Chiller.ttf'))



class ImageLayout(BoxLayout):   #defined in the kv file

    pass


class TextLayout(BoxLayout):    #defined in the kv file

    pass


class ButtonLayout(BoxLayout):  #defined in the kv file

    pass


class TitleLabel(Label):        #defined in the kv file

    pass


class NieblaButton(Button):

    def __init__(self, fate, consequences, **kwargs):
        super().__init__(**kwargs)

        self.fate = fate
        self.consequences = consequences



class NieblaApp(App):

    story = autorol_utils.read_json(get_resource_path('Niebla.json'))   

    scenes = autorol_utils.get_scenes(story, format=True)  #Format True removes html tags and introduces kivy markups

    title = story['titulo']
    
    all_variables = autorol_utils.get_variables(scenes)
    
    current_scene = autorol_utils.get_intro(scenes)

    scroll = ScrollView()

    

####################################################### MAIN 'LOOP' #############################################################



    def build (self):


        layout = BoxLayout()
        
        textlayout = TextLayout()

        buttonlayout = ButtonLayout()

        self.place_text(textlayout)    

        self.place_buttons(buttonlayout)

        layout.add_widget(textlayout)

        layout.add_widget(buttonlayout)

        self.scroll.add_widget(layout)

        return self.scroll
    


    ############################################### PLACE TEXT AND IMAGES #####################################################

    

    def place_text(self, layout):


        if self.current_scene['id'] == autorol_utils.get_intro(self.scenes, id_only=True): #if start of the game, add title
            
            titledisplay = TitleLabel(text = self.title)

            layout.add_widget(titledisplay)


        
        text_object = autorol_utils.get_text(self.current_scene)

            
        for text in text_object:

            conditions = autorol_utils.get_conditions(text)


            if autorol_utils.compare_conditions(self.all_variables, conditions):


                if text['texto'][:8] == '[$image]':     #if text is an image
                    
                    display = ImageLayout()             #images must be embedded in BoxLayouts in order to specify padding
                    
                    image_path = get_resource_path('pics/'+ text['texto'][8:])     #image folder must be named 'pics'

                    image_display = Image(source = image_path)  #create Image label

                    display.add_widget(image_display)           #embed Image label in BoxLayout


                else:                                   #if text is a text
                
                    display = Label(text = autorol_utils.align(text['texto'])[0], halign = autorol_utils.align(text['texto'])[1])

                
                
                consequences = autorol_utils.get_consequences(text) #consequences are checked for both texts and images

                self.all_variables.update (consequences)
                
                layout.add_widget(display)



    ################################################ PLACE BUTTONS ############################################################## 


    
    def place_buttons (self, layout):

        
        text_object = autorol_utils.get_text(self.current_scene)

        linked_texts = 0

        for text in text_object:

            links = autorol_utils.get_links(text)

            if len(links) > 0:      #this checks if all the snippets of text of the section have no links
            
                linked_texts += 1 

            
        if linked_texts == 0:     #if end of the game a restart button is created leading to the intro

            intro_id = autorol_utils.get_intro(self.scenes, id_only=True)

            links = [{'texto': 'Volver a empezar', 
                          'destinoExito': intro_id,
                          'consecuencias': [],
                          'condiciones': []}]
                
            self.all_variables = {key: 0 for key in self.all_variables}     #sets to 0 all variables of the game
            
            
        for link in links:

            conditions = autorol_utils.get_conditions(link)

            if autorol_utils.compare_conditions(self.all_variables, conditions):    #place button if conditions are met

                button = NieblaButton(text=link['texto'], fate = link['destinoExito'], consequences=autorol_utils.get_consequences(link))

                button.bind(on_release = self.on_button_release)

                layout.add_widget(button)

           

    ######################################## DEFINE BUTTON PRESS ####################################################################



    def on_button_release(self, instance):  #'instance' refers to the particular button created (instance of Button class)

        self.all_variables.update(instance.consequences)

        self.current_scene = autorol_utils.get_scene(int(instance.fate), self.scenes)

        self.rebuild()



    def rebuild(self):

        self.scroll.clear_widgets()

        self.build ()

        self.scroll.scroll_y = 1.0          #brings scroll back to the top

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    NieblaApp().run()