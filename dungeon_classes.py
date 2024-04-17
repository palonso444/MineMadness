from kivy.uix.gridlayout import GridLayout    # type: ignore


import crapgeon_utils as utils
import character_classes as characters
import token_classes as tokens
import tile_classes as tiles
from collections import deque


class DungeonLayout(GridLayout):    #initialized in kv file

    
    def on_pos(self, *args):
    
        
        self.generate_blueprint(self.rows, self.cols)   #initialize map of dungeon
        
        
        for y in range (self.rows):
              
                for x in range (self.cols):

                    if self.blueprint[y][x] == ' ':

                        tile = tiles.Tile(row=y, col=x, kind ='exit', dungeon_instance=self)

                    else:

                        tile = tiles.Tile(row=y, col=x, kind ='floor', dungeon_instance=self)
                
                    self.add_widget(tile)


        self.game = self.parent.parent
        self.game.dungeon = self  #Adds dungeon as CrapgeonGame class attribute
        

    def generate_blueprint (self, height, width):

        self.blueprint = utils.create_map(height, width)

        utils.place_single_items(self.blueprint,'K', 2)  #rats
        utils.place_single_items(self.blueprint,'H', 2)  #hellhound
        utils.place_single_items(self.blueprint,'W', 2)  #djinn

        utils.place_single_items(self.blueprint,'%', 1, (2,2))
        utils.place_single_items(self.blueprint,'o', 0)
        utils.place_single_items(self.blueprint,' ', 0)

        for key,value in {'M': 0, '#': 0.3, 'p': 0, 'x': 0, 's': 0}.items():  #.items() method to iterate over key and values, not only keys (default)
        
            utils.place_items (self.blueprint, item=key, frequency=value)

        
        #for y in range (len(self.blueprint)):
                #print (*self.blueprint[y])
    
    

    def allocate_tokens (self):

        for tile in self.children:
        
            with self.canvas:

                if self.blueprint [tile.row][tile.col] == '%':

                    self.place_tokens(tile, 'player')
                        

                elif self.blueprint [tile.row][tile.col] == 'K':
                        
                    self.place_tokens(tile, 'monster', 'kobold')

                elif self.blueprint [tile.row][tile.col] == 'H':
                        
                    self.place_tokens(tile, 'monster', 'hound')

                elif self.blueprint [tile.row][tile.col] == 'W':
                        
                    self.place_tokens(tile, 'monster', 'wisp')

                    
                elif self.blueprint [tile.row][tile.col] == '#':

                    self.place_tokens(tile, 'wall')

                
                elif self.blueprint [tile.row][tile.col] == 'p':

                    self.place_tokens(tile, 'shovel')

                elif self.blueprint [tile.row][tile.col] == 'x':

                    self.place_tokens(tile, 'weapon')

                
                elif self.blueprint [tile.row][tile.col] == 'o':

                    self.place_tokens(tile, 'gem')


    def place_tokens(self, tile, token_kind, token_species = None):

        if token_species:
            token_source = token_species + 'token.png'
        else:
            token_source = token_kind + 'token.png'
        
        #PLACE CHARACTERS
        if self.blueprint [tile.row][tile.col] in characters.Character.blueprint_ids:
        
            tile.token = tokens.CharacterToken(source = token_source,
                                 position = (tile.row, tile.col),  
                                 kind = token_kind,
                                 species = token_species,
                                 dungeon_instance = self,
                                 character = None,
                                 pos = tile.pos,
                                 size = tile.size)
        
        
            if token_kind == 'player':
                
                character = characters.Vane()

            
            elif token_kind == 'monster':

                if token_species == 'kobold':
                
                    character = characters.Kobold()
                
                elif token_species == 'hound':
                
                    character = characters.HellHound()

                elif token_species == 'wisp':
                
                    character = characters.DepthsWisp()
            
            character.position = (tile.row, tile.col)   #Character attributes initialized here
            character.token = tile.token
            character.dungeon = self
            character.id = len(character.__class__.data)
            character.__class__.data.append (character)
            
            tile.token.character = character


        #PLACE SCENERY
        else:

            tile.token = tokens.SceneryToken(source = token_source,
                                 position = (tile.row, tile.col),  
                                 kind = token_kind,
                                 dungeon_instance = self,
                                 pos = tile.pos,
                                 size = tile.size)


    def activate_which_tiles(self, tile_positions = None):

        for tile in self.children:

            tile.disabled = True

            if tile_positions:
            
                for position in tile_positions:

                    if tile.row == position[0] and tile.col == position[1] and tile.is_activable():
                        
                        tile.disabled = False

    
    def get_tile(self, position):

        for tile in self.children:

            if tile.position == position:
                
                return tile

    
    def scan(self, scenery):    #pass scenery as tuple of token.kinds to look for (e.g. ('wall', 'shovel'))

        
        found_tiles = set()
        
        for tile in self.children:

            if tile.token and tile.token.kind in scenery:

                found_tiles.add((tile.row, tile.col))

            elif tile.monster_token and tile.monster_token.kind in scenery:

                found_tiles.add((tile.row, tile.col))

        
        return found_tiles


    def find_shortest_path(self, start_tile, end_tile, exclude = tuple()):     #USE WHEN GETTING MOVEMENT RANGE 
                                                            #(if shortest path longer than moves, do not activate tile)
        
        start_tile_pos, end_tile_pos = (start_tile.row, start_tile.col), (end_tile.row, end_tile.col)

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = deque([(start_tile_pos, [])]) # start_tile_pos is not included in the path
        excluded_tiles = set()
        
        for position in self.scan(exclude):  #scan dungeon for occupied tiles
            excluded_tiles.add(position)
        
        excluded_tiles.add(start_tile_pos)

        while queue:
  
            current_pos, path =  queue.popleft()
            
            for direction in directions:

                row, col = current_pos[0] + direction[0], current_pos[1] + direction[1] # explore one step in all 4 directions

                if 0 <= row < self.rows and 0 <= col < self.cols and (row, col) not in excluded_tiles:
                    
                    excluded_tiles.add((row, col))
                    queue.append(((row,col), path + [(row,col)]))

            if current_pos == end_tile_pos:

                return path