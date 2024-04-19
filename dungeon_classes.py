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

        utils.place_single_items(self.blueprint,'K', 0)  #rats
        utils.place_single_items(self.blueprint,'H', 0)  #hellhound
        utils.place_single_items(self.blueprint,'W', 0)  #wisp
        utils.place_single_items(self.blueprint,'N', 14)  #nightmare

        utils.place_single_items(self.blueprint,'%', 1, (0,0))
        utils.place_single_items(self.blueprint,'o', 0)
        utils.place_single_items(self.blueprint,' ', 0)

        for key,value in {'M': 0, '#': 0.5, 'p': 0.3, 'x': 0.3, 's': 0}.items():  #.items() method to iterate over key and values, not only keys (default)
        
            utils.place_items (self.blueprint, item=key, frequency=value)

        
        #for y in range (len(self.blueprint)):
                #print (*self.blueprint[y])
    
    

    def allocate_tokens (self):

        for tile in self.children:
        
            with self.canvas:

                if self.blueprint [tile.row][tile.col] == '%':

                    self.place_tokens(tile, 'player', 'vane')
                        

                elif self.blueprint [tile.row][tile.col] == 'K':
                        
                    self.place_tokens(tile, 'monster', 'kobold')

                elif self.blueprint [tile.row][tile.col] == 'H':
                        
                    self.place_tokens(tile, 'monster', 'hound')

                elif self.blueprint [tile.row][tile.col] == 'W':
                        
                    self.place_tokens(tile, 'monster', 'wisp')

                elif self.blueprint [tile.row][tile.col] == 'N':
                        
                    self.place_tokens(tile, 'monster', 'nightmare')

                    
                elif self.blueprint [tile.row][tile.col] == '#':

                    self.place_tokens(tile, 'wall')

                
                elif self.blueprint [tile.row][tile.col] == 'p':

                    self.place_tokens(tile, 'shovel')

                elif self.blueprint [tile.row][tile.col] == 'x':

                    self.place_tokens(tile, 'weapon')

                
                elif self.blueprint [tile.row][tile.col] == 'o':

                    self.place_tokens(tile, 'gem')


    def place_tokens(self, tile, token_kind, token_species = None):


        if token_kind == 'player' or token_kind == 'monster':
        
            if token_kind == 'player':

                if token_species == 'vane':
                    character = characters.Vane()

            
            elif token_kind == 'monster':

                if token_species == 'kobold':
                    character = characters.Kobold()
                
                elif token_species == 'hound':
                    character = characters.HellHound()

                elif token_species == 'wisp':
                    character = characters.DepthsWisp()

                elif token_species == 'nightmare':
                    character = characters.NightMare()

            tile.token = tokens.CharacterToken(position = (tile.row, tile.col),  
                                 kind = token_kind,
                                 species = token_species,
                                 dungeon_instance = self,
                                 character = None,
                                 pos = tile.pos,
                                 size = tile.size)
            
            character.position = (tile.row, tile.col)   #Character attributes initialized here
            character.token = tile.token
            character.dungeon = self
            character.id = len(character.__class__.data)
            character.__class__.data.append (character)
            
            tile.token.character = character


        else:

            tile.token = tokens.SceneryToken(position = (tile.row, tile.col),  
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

    
    def scan(self, scenery, exclude = False):    #pass scenery as tuple of token.kinds to look for (e.g. ('wall', 'shovel'))

        
        found_tiles = set()

        excluded_tiles = set()
        
        for tile in self.children:

            for token in scenery:

                if not exclude and tile.has_token(token):

                    found_tiles.add(tile.position)

                elif exclude and tile.has_token(token):

                    excluded_tiles.add(tile)

        if exclude:

            for tile in self.children:

                if tile not in excluded_tiles:

                    found_tiles.add(tile.position)

        return found_tiles


    def find_shortest_path(self, start_tile, end_tile, excluded = tuple()):
                                                            

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        queue = deque([(start_tile.position, [])]) # start_tile_pos is not included in the path

        excluded_tiles = self.scan(excluded)
        excluded_tiles.add(start_tile.position)

        while queue:
  
            current_position, path =  queue.popleft()

            if current_position == end_tile.position:

                return path
            
            for direction in directions:

                row, col = current_position[0] + direction[0], current_position[1] + direction[1] # explore one step in all 4 directions

                if 0 <= row < self.rows and 0 <= col < self.cols: 
                    
                    if (row, col) not in excluded_tiles or (row,col) == end_tile.position:
    
                        excluded_tiles.add((row, col))
                        queue.append(((row,col), path + [(row,col)]))

    def find_closest_free_tiles(self, target_tile, cannot_share, blocked_by): #excluded tokens as tuple

        paths = list()
        
        #look for free tiles in the dungeon
        scanned = self.scan(cannot_share, exclude = True)  

        
        #find paths from player to all free tiles scanned
        for tile_position in scanned:

            scanned_tile = self.get_tile(tile_position)
            path = self.find_shortest_path(target_tile, scanned_tile, blocked_by)

            if path:

                end_tile = self.get_tile(path[-1])

                if not end_tile.monster_token:
                
                    if not end_tile.token or end_tile.token.kind not in self.cannot_share_tile_with:
                        paths.append(path)
        pass