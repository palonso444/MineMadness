from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty

class MainMenu(Screen):
    pass

class HowToPlay(Screen):
    pass

class OutGameOptions(Screen):
    pass

class InGameOptions(Screen):
    pass

class NewGameConfig(Screen):
    pass

class GameOver(Screen):
    pass

class CharacterProgressionMenu(Screen):
    background = ObjectProperty(None, allownone=True)

class LoadingScreen(Screen):
    pass
