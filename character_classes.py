


class Character:

    blueprint_ids = ('%', 'R', 'H')

    
    def __init__(self, position, moves, token, id):    #position as tuple (y,x)
        
        self.position = position
        self.moves = moves
        self.token = token
        self.dungeon = self.token.dungeon
        self.id = id

    
    def update_position (self, y_position, x_position):

        self.__class__.data[self.id].position = (y_position, x_position)
        self.__class__.data[self.id].token.position = (y_position, x_position)

    
    def rearrange_ids (self):

        for character in self.__class__.data:

            if character.id > self.id:

                character.id -= 1


class Player(Character):

    data = list ()
    blueprint_ids = ['%']

    def __init__(self, position, moves, token, id, health, shovels = 0, weapons = 0, gems = 0):
        super().__init__(position, moves, token, id)

        self.remaining_moves = 0
        self.health = health
        self.shovels = shovels
        self.weapons = weapons
        self.gems = gems

    
    
    def get_movement_range(self, dungeon_layout):   #TODO: DO NOT ACTIVATE IF WALLS ARE PRESENT
                                                    #TODO: better as method of Player Class

        def get_lateral_range(self, y_position, side_move, mov_range, dungeon_layout):

            
            if self.position[1] - side_move >= 0: #if room in left side

                mov_range.add((y_position, self.position [1] - side_move)) #one step left.

            
            if self.position[1] + side_move < dungeon_layout.cols: #if room in right side             

                mov_range.add((y_position, self.position [1] + side_move)) #one step right


        mov_range = set()  #set of tuples (no repeated values)
        remaining_moves = self.remaining_moves
        
        # GET CURRENT PLAYER POSITION
        mov_range.add((self.position[0], self.position[1]))
        

        for move in range (1, remaining_moves + 1):     #starts at 1 not to include current player position again

            #INCLUDE ALL POSSIBLE MOVES ON THE SAME ROW AS PLAYER
            get_lateral_range(self, self.position[0], move, mov_range, dungeon_layout)
            remaining_moves -= 1
            
            if self.position[0] - move >= 0:    #if height within range up

                #INCLUDE ALL POSSIBLE MOVES DIRECTION UP
                mov_range.add((self.position[0] - move, self.position[1]))  #one step up. 

                for side_move in range(1, remaining_moves + 1):         #one step both sides

                    get_lateral_range(self, self.position[0] - move, side_move, mov_range, dungeon_layout)


            if self.position[0] + move < dungeon_layout.rows:   #if height within range down
            
                #INCLUDE ALL POSSIBLE MOVES DIRECTION DOWN
                mov_range.add((self.position[0] + move, self.position[1]))   #one step down.

                for side_move in range(1, remaining_moves + 1):         #one step both sides

                    get_lateral_range(self, self.position[0] + move, side_move, mov_range, dungeon_layout)
        
        
        return mov_range

    
class Monster(Character):

    data = list()
    #blueprint_ids = ['M']

    def __init__(self, position, moves, token, id):
        super().__init__(position, moves, token, id)
        self.kind = 'monster'
        self.blocked_by = ('wall')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')

    
    def find_closest_player(self):


        distances = list()
        
        for player in Player.data:
        
            distance = abs(self.position[0] - player.position[0]) + abs(self.position[1] - player.position[1])
            
            distances.append(distance)

        shortest_distance = min(distances)

        for distance in distances:

            if distance == shortest_distance:

                return Player.data[distances.index(distance)]


    def assess_path_direct(self):

        target = self.find_closest_player() #REDO SO IT CAN TARGET ALSO GEMS, FOR INSTANCE

        path = list()

        position = self.position
        
        for moves in range (self.moves):

            #CHECKS WHICH DIRECION IS THE PLAYER AND CHECKS IF TILES ARE FREE
            if target.position[0] < position[0] and self.goes_through(self.dungeon.get_tile((position[0] -1, position[1]))):
                
                position = (position[0] -1, position [1])
                path.append(position)
            
            elif target.position[0] > position[0] and self.goes_through(self.dungeon.get_tile((position[0] +1, position[1]))):
                
                position = (position[0] +1, position [1])
                path.append(position)
            
            elif target.position[1] < position[1] and self.goes_through(self.dungeon.get_tile((position[0], position[1] - 1))):
 
                position = (position[0],position [1]-1)
                path.append(position)
            
            elif target.position[1] > position[1] and self.goes_through(self.dungeon.get_tile((position[0], position[1] + 1))):
                
                position = (position[0], position[1]+1)
                path.append(position)
        
        path = self.check_free_landing(path)
        
        if len(path) == 0:
            path = [self.position]

        return path
    

    def goes_through(self, tile):
        
        
        if tile.token and tile.token.kind in self.blocked_by:
            return False
        if tile.monster_token and tile.monster_token.kind in self.blocked_by:
            return False
               
        return True
    
    
    def check_free_landing(self, path):

        
        for position in reversed(path):
        
            for token_kind in self.cannot_share_tile_with:
        
                if len(path)>0 and self.dungeon.get_tile(path[-1]).has_token(token_kind):

                        path.remove(position)

        return path