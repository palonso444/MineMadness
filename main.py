from kivy.app import App    # type: ignore
from kivy.uix.boxlayout import BoxLayout    # type: ignore
from kivy.uix.gridlayout import GridLayout    # type: ignore
#from kivy.uix.scrollview import ScrollView  # type: ignore
from kivy.uix.label import Label    # type: ignore
from kivy.uix.button import Button  # type: ignore
#from kivy.core.text import LabelBase    # type: ignore
#from kivy.uix.image import Image    # type: ignore
from kivy.graphics import Ellipse   # type: ignore
from kivy.uix.widget import Widget  # type: ignore
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty, Clock   # type: ignore
from kivy.animation import Animation


import crapgeon_utils as utils
import crapgeon_classes as classes
from collections import deque


#LabelBase.register(name = 'Vollkorn',
                   #fn_regular= 'fonts/Vollkorn-Regular.ttf',
                   #fn_italic='fonts/Vollkorn-Italic.ttf'



class Token(Ellipse):

    
    def __init__(self, position, kind, dungeon_instance, character, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if monster, player, wall, etc.
        self.position = position
        self.dungeon = dungeon_instance
        self.character = character      #links token with character object
        self.start = None   #defined when token is moved by dungeon move_token
        self.goal = None    #defined when token is moved by dungeon move_token


    def move (self, start_tile, end_tile):

        
        self.start = start_tile

        self.goal = end_tile
        
        Clock.schedule_interval(self.slide, 1/60)   #60 fps

    
    def slide (self, dt):   #pos are computed here as (x, y), default kivy, reverse than usual

        speed = 4

        self.dungeon.activate_which_tiles() #tiles inactivated while sliding

        #path = self.dungeon.find_shortest_path(self.pos, self.goal)

        #if len(path) > 0:

            #int_goal = path.pop(0)

        #TO AVOID SMALL POSITION INACCURACIES. CAN BE REMOVED ONCE COMMENTED CODE IS IMPLEMENTED
        if int(self.pos[0]) != int(self.goal.pos[0]) or int(self.pos[1]) != int(self.goal.pos[1]):

            #SLIDE HORIZONTALLY
            if self.pos[0] < self.goal.pos [0]: #RIGHT
                self.pos = (self.pos[0]+speed, self.pos[1])

            elif self.pos[0] > self.goal.pos [0]: #LEFT
                self.pos = (self.pos[0]-speed, self.pos[1])

            #SLIDE VERTICALLY
            elif self.pos[1] < self.goal.pos [1]: #RIGHT
                self.pos = (self.pos[0], self.pos[1]+speed)

            elif self.pos[1] > self.goal.pos [1]: #LEFT
                self.pos = (self.pos[0], self.pos[1]-speed)

        else:   #movement is complete

            if self.goal.token is not None:

                if self.check_collision(self.goal.token):

                    self.goal.token.character.rearrange_ids()
            
            self.update_on_tiles(self.start, self.goal) #updates tile.token of start and goal

            self.character.update_position(self.goal.row, self.goal.col)

            self.dungeon.game.next_character() #switch turns if character last of character.characters list

            return False    #this prevents the event from rescheduling itself

    
    def update_on_tiles(self, start_tile, end_tile):

        start_tile.token = None
        end_tile.token = self

    
    def check_collision(self, other_token):

        if self.kind == 'player':

            if self.goal.token.kind == 'monster':

                classes.Monster.data.remove(self.goal.token.character)

                self.dungeon.canvas.remove(self.goal.token)

                #self.goal.token = None

                return True

            else:

                print ('PLAYERS GREET EACH OTHER')
                return False

        elif self.kind == 'monster':

            if self.goal.token.kind == 'player':

                classes.Player.data.remove(self.goal.token.character)

                print (len(classes.Player.data))

                self.dungeon.canvas.remove(self.goal.token)

                #self.goal.token = None

                return True 

            else:

                print ('MONSTERS GREET EACH OTHER')
                return False




  
class DungeonTile(Button):

    
    def __init__(self, row, col, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.row = row
        self.col = col
        self.token = None   #defined later when token is placed on tile by DungeonLayout.place_tokens
        self.dungeon = dungeon_instance     #need to pass the instance of the dungeon in order to cal dungeon.move_token from this class


    def bind_token (self, *args):
        
        self.token.pos = self.pos
        self.token.size = self.size


    def on_release(self):

        active_character = self.dungeon.game.active_character
        
        start_position = (active_character.position[0], active_character.position[1])
        
        start_tile = self.dungeon.get_tile(start_position[0], start_position[1])

        start_tile.token.move(start_tile, self)




class DungeonLayout(GridLayout):    #initialized in kv file


    #def __init__(self, **kwargs):
        #super().__init__(**kwargs)
        
        #self.blueprint = self.generate_blueprint(height, width)
        #self.rows = height
        #self.cols = width

    
    def on_pos(self, *args):
    
        for y in range (self.rows):
              
                for x in range (self.cols):
                    
                    tile = DungeonTile(row=y, col=x, dungeon_instance=self)
                
                    self.add_widget(tile)

                    print ('TILES ADDED')

        
        self.generate_blueprint(self.rows, self.cols)

        self.game = self.parent.parent

        self.game.dungeon = self  #Adds dungeon as CrapgeonGame class attribute

        #self.parent.parent.dungeon = self  #Adds dungeon as CrapgeonGame class attribute
        


    def generate_blueprint (self, height, width):

        dungeon_blueprint = utils.create_map(height, width)

        utils.place_single_items(dungeon_blueprint,'M', 3)
        utils.place_single_items(dungeon_blueprint,'%', 2)
        utils.place_single_items(dungeon_blueprint,'o', 5)
        utils.place_single_items(dungeon_blueprint,' ', 1)

        for key,value in {'M': 0, '#': 0.6, 'p': 0.05, 'x': 0.05, 's': 0.02}.items():  #.items() method to iterate over key and values, not only dkeys (default)
        
            utils.place_items (dungeon_blueprint, item=key, frequency=value)

        self.blueprint = dungeon_blueprint
    

    def allocate_tokens (self):

        for tile in self.children:

            if self.blueprint [tile.row][tile.col] in classes.Character.blueprint_ids:
        
                with self.canvas:

                    if self.blueprint [tile.row][tile.col] == '%':

                        self.place_tokens(tile, 'player')
                        

                    elif self.blueprint [tile.row][tile.col] == 'M':

                        self.place_tokens(tile, 'monster')


    def place_tokens(self, tile, token_kind):

        
        if token_kind == 'player':
            token_source = 'playertoken.png'
        elif token_kind == 'monster':
            token_source = 'monstertoken.png'
        
        
        tile.token = Token(source = token_source, 
                                 position = (tile.row, tile.col),  
                                 kind = token_kind,
                                 dungeon_instance = self,
                                 character = None)
        
        if token_kind == 'player':
            character = classes.Player (position = (tile.row, tile.col), #create player object
                                     moves = 4,
                                     token = tile.token,
                                     id = len(classes.Player.data))

        elif token_kind == 'monster':
            character = classes.Monster(position = (tile.row, tile.col), 
                                      moves = 1,
                                      token = tile.token,
                                      id = len(classes.Monster.data))   #create monster object
            

        character.__class__.data.append (character)   #create monster to monsters list
        tile.token.character = character
        tile.bind (pos = tile.bind_token, size = tile.bind_token)


    def activate_which_tiles(self, tile_positions = None):

        for tile in self.children:

            tile.disabled = True

            if tile_positions is not None:
            
                for position in tile_positions:

                    if tile.row == position[0] and tile.col == position[1]:

                        tile.disabled = False

    
    def get_tile(self, row, col):

        for tile in self.children:

            if tile.row == row and tile.col == col:
                
                return tile


    def find_shortest_path(self, start_tile, end_tile):     #USE WHEN GETTING MOVEMENT RANGE 
                                                            #(if shortest path longer than moves, do not activate tile)
        
        start_tile_pos, end_tile_pos = (start_tile.row, start_tile.col), (end_tile.row, end_tile.col)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = deque([(start_tile_pos, [])]) # start_tile_pos is not included in the path
        tiles_visited = set()
        tiles_visited.add(start_tile_pos)

        while queue:
  
            current_pos, path =  queue.popleft()
            
            if current_pos == end_tile_pos:

                return (path)
            
            for direction in directions:

                row, col = current_pos[0] + direction[0], current_pos[1] + direction[1] # explore one step in all 4 directions

                if 0 <= row < self.rows and 0 <= col < self.cols and (row, col) not in tiles_visited:
 
                    tiles_visited.add((row, col))
                    queue.append(((row,col), path + [(row,col)]))



class CrapgeonGame(BoxLayout):  #initlialized in kv file

    
    active_character_id = NumericProperty(None)

    dungeon = ObjectProperty(None)
    


    def on_dungeon(self, *args):

        print ('POPULATING DUNGEON')

        self.dungeon.allocate_tokens()

        self.turn = True    #TRUE for players, FALSE for monsters. Player starts
        
        self.active_character_id = 0    #starts first character on players.data

        print ('MONSTERS')
        print (len(classes.Monster.data))
        print ('\nPLAYERS')
        print (len(classes.Player.data))

    
    def next_character(self):


        if self.active_character.id == len(self.active_character.__class__.data) - 1:  #if all players or monsters have moved
            
            self.turn = not self.turn   #turn changes
            
            self.active_character_id = 0

        
        else: 
            
            self.active_character_id += 1       # next character on list moves


    def on_active_character_id (self, *args):

        
        if self.turn:   #if player turn
        
            #print ('\n\nPLAYERS TURN')

            #print (classes.Player.data[0].position)

            self.active_character = classes.Player.data[self.active_character_id]
            
            movement_range = self.active_character.get_movement_range(self.dungeon)

            self.dungeon.activate_which_tiles(movement_range)

        
        elif not self.turn:       #if monsters turn
        
            #print ('\n\nMONSTERS TURN')

            self.active_character = classes.Monster.data[self.active_character_id]
                
            start_tile = self.dungeon.get_tile(self.active_character.position[0], self.active_character.position[1])

            self.active_character.assess_move_direct()    #CHANGE TARGET CLOSEST PLAYER

            end_tile = self.dungeon.get_tile(self.active_character.position[0], self.active_character.position[1])      
    
            self.active_character.token.move(start_tile, end_tile)
        


class CrapgeonApp(App):

    def build (self):

        return CrapgeonGame()

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()