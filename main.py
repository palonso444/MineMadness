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
from kivy.properties import ListProperty, BooleanProperty, ObjectProperty, Clock   # type: ignore
from kivy.animation import Animation


import crapgeon_utils as utils
import crapgeon_classes as classes
from collections import deque


#LabelBase.register(name = 'Vollkorn',
                   #fn_regular= 'fonts/Vollkorn-Regular.ttf',
                   #fn_italic='fonts/Vollkorn-Italic.ttf'



class Token(Ellipse):   #Tokens have id that identifies them (as Monsters or Player)

    
    def __init__(self, position, kind, id, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.kind = kind    #defines if monster, player, wall, etc.
        self.id = id        #defines index in monsters or players lists
        self.position = position
        self.dungeon = dungeon_instance
        self.start = None   #defined when token is moved by dungeon move_token
        self.goal = None    #defined when token is moved by dungeon move_token

    
    def slide (self, dt):   #pos are computed here as (x, y), default kivy, reverse than usual

        speed = 4

        self.dungeon.activate_tiles() #tiles inactivated while sliding

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

        else:

            self.update_on_tiles(self.start, self.goal) #updates tile.token of start and goal

            print (self.id)

            classes.Character.update_position(self.goal.row, self.goal.col, self.kind, self.id)

            #CHANGE TO FUNCTION UPDATE DATABASE MONSTERS AND PLAYER
            #if self.kind == 'player':
                #classes.Player.players[0].position = (self.goal.row, self.goal.col)

            #if self.kind == 'monster':
                #classes.Monster.monsters[0].position = (self.goal.row, self.goal.col)

            self.dungeon.parent.switch_turn()

            return False    #this prevents the event from rescheduling itself

    
    def update_on_tiles(self, start_tile, end_tile):

        start_tile.token = None
        end_tile.token = self


  
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

        start_position = (classes.Player.players[0].position[0], classes.Player.players[0].position[1])
        
        start_tile = self.dungeon.get_tile(start_position[0], start_position[1])
        
        self.move_token(start_tile = start_tile, end_tile=self)
        

    def move_token(self, start_tile, end_tile):

        
        start_tile.token.start = start_tile

        start_tile.token.goal = end_tile
        
        Clock.schedule_interval(start_tile.token.slide, 1/60)   #60 fps

        #self.update_token(start_tile, end_tile)



    def update_tile_tokens (self, start_tile, end_tile):  #DEPRECATED
        
        pass

        #temporal_token = start_tile.token # to avoid error if tile button where player is is clicked
        
        #start_tile.token = None
        #end_tile.token = temporal_token




class DungeonLayout(GridLayout):


    def __init__(self, height, width, **kwargs):
        super().__init__(**kwargs)
        
        self.blueprint = self.generate_blueprint(height, width)
        self.rows = height
        self.cols = width
        self.tokens = list()

        for y in range (self.rows):
              
            for x in range (self.cols):
                
                tile = DungeonTile(row=y, col=x, dungeon_instance=self)
                
                self.add_widget(tile)


    def generate_blueprint (self, height, width):

        dungeon_blueprint = utils.create_map(height, width)

        utils.place_single_items(dungeon_blueprint,'M', 1, (0,0))
        utils.place_single_items(dungeon_blueprint,'%', 1, (3,3))
        utils.place_single_items(dungeon_blueprint,'o', 5)
        utils.place_single_items(dungeon_blueprint,' ', 1)

        for key,value in {'M': 0, '#': 0.6, 'p': 0.05, 'x': 0.05, 's': 0.02}.items():  #.items() method to iterate over key and values, not only dkeys (default)
        
            utils.place_items (dungeon_blueprint, item=key, frequency=value)

        return dungeon_blueprint
    

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
            token_id = len(classes.Player.players)
            player = classes.Player (position = (tile.row, tile.col), moves = 2)    #create player object
            classes.Player.players.append (player)  #add player to players list

        elif token_kind == 'monster':
            token_source = 'monstertoken.png'
            token_id = len(classes.Monster.monsters)
            monster = classes.Monster(position = (tile.row, tile.col), moves = 1)   #create monster object
            classes.Monster.monsters.append (monster)   #create monster to monsters list

        tile.token = Token(source = token_source, 
                                 position = (tile.row, tile.col),  
                                 kind = token_kind, 
                                 id = token_id,
                                 dungeon_instance = self)
        
        self.tokens.append(tile.token)    #add tokens to tokens list in DungeonLayout
        tile.bind (pos = tile.bind_token, size = tile.bind_token)


    def activate_tiles(self, tile_positions = None):

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



class CrapgeonGame(BoxLayout):

    turn = BooleanProperty(None)    #TRUE for player, FALSE for monsters


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        print ('EXECUTING CRAPGEONGAME__INIT__')
        
        self.dungeon = DungeonLayout(10,10) #dungeon is attribute of app so move_token() can be called from kv file.

        self.dungeon.allocate_tokens()
      
        self.add_widget(self.dungeon)

        self.turn = True          #player starts

        #print (len(classes.Monster.monsters))
        #print (len(classes.Player.players))

    
    def switch_turn(self):

        #print ('TURN SWITCHED')
        
        self.turn = not self.turn

    
    def on_turn (self, instance, value):

        
        if value:   #if player turn
        
            #print ('\n\nPLAYERS TURN')

            #print (classes.Player.players[0].position)

            movement_range = classes.Player.players[0].get_movement_range(self.dungeon)

            #print (movement_range)

            self.dungeon.activate_tiles(movement_range)

        elif not value:       #if monsters turn
        
            #print ('\n\nMONSTERS TURN')


            for monster in classes.Monster.monsters:

                start_tile = self.dungeon.get_tile(monster.position[0], monster.position[1])

                monster.assess_move_direct(classes.Player.players[0])

                end_tile = self.dungeon.get_tile(monster.position[0], monster.position[1])

                end_tile.move_token(start_tile, end_tile)
        


class CrapgeonApp(App):

    def build (self):

        return CrapgeonGame()

    

######################################################### START APP ##########################################################



if __name__ == '__main__':
    CrapgeonApp().run()