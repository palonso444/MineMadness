

class Character:

    blueprint_ids = ['%', 'M']

    
    def __init__(self, position, moves, token, id):    #position as tuple (y,x)
        
        self.position = position
        self.moves = moves
        self.token = token
        self.id = id


    def get_movement_range(self, dungeon_layout):   #TODO: DO NOT ACTIVATE IF WALLS ARE PRESENT
                                                    #TODO: better as method of Player Class

        
        mov_range = set()  #set of tuples (no repeated values)
        remaining_moves = self.moves
        
        # GET CURRENT PLAYER POSITION
        mov_range.add((self.position[0], self.position[1]))
        

        for move in range (1, remaining_moves + 1):     #starts at 1 not to include current player position again

            #INCLUDE ALL POSSIBLE MOVES ON THE SAME ROW AS PLAYER
            self.get_lateral_range(self.position[0], move, mov_range, dungeon_layout)
            remaining_moves -= 1
            
            if self.position[0] - move >= 0:    #if height within range up

                #INCLUDE ALL POSSIBLE MOVES DIRECTION UP
                mov_range.add((self.position[0] - move, self.position[1]))  #one step up. 

                for side_move in range(1, remaining_moves + 1):         #one step both sides

                    self.get_lateral_range(self.position[0] - move, side_move, mov_range, dungeon_layout)


            if self.position[0] + move < dungeon_layout.rows:   #if height within range down
            
                #INCLUDE ALL POSSIBLE MOVES DIRECTION DOWN
                mov_range.add((self.position[0] + move, self.position[1]))   #one step down.

                for side_move in range(1, remaining_moves + 1):         #one step both sides

                    self.get_lateral_range(self.position[0] + move, side_move, mov_range, dungeon_layout)
        
        
        return mov_range


    def get_lateral_range(self, y_position, side_move, mov_range, dungeon_layout):

            
            if self.position[1] - side_move >= 0: #if room in left side

                mov_range.add((y_position, self.position [1] - side_move)) #one step left.

            
            if self.position[1] + side_move < dungeon_layout.cols: #if room in right side             

                mov_range.add((y_position, self.position [1] + side_move)) #one step right

    
    def update_position (self, y_position, x_position):

        self.__class__.data[self.id].position = (y_position, x_position)

    
    def rearrange_ids (self):

        for character in self.__class__.data:

            if character.id > self.id:

                character.id -= 1


class Player(Character):

    data = list ()
    blueprint_ids = ['%']

    def __init__(self, position, moves, token, id):
        super().__init__(position, moves, token, id)


class Monster(Character):

    data = list()
    blueprint_ids = ['M']

    def __init__(self, position, moves, token, id):
        super().__init__(position, moves, token, id)
        self.kind = 'monster'


    def assess_move_direct(self):


        target = self.find_closest_player()

        
        for move in range (self.moves):


            if target.position[0] < self.position[0]: #and map[self.position[0]-1] [self.position[1]] == '.':
				   
                new_position = (self.position[0] -1, self.position [1])
            
            elif target.position[0] > self.position[0]: #and (map[self.position[0] +1][self.position[1]] == '.'):
            
                new_position = (self.position[0] +1, self.position [1])
            
            elif target.position[1] < self.position[1]: #and map[self.position[0]][self.position[1] -1] == '.':
            
                new_position = (self.position[0],self.position [1]-1)
            
            elif target.position[1] > self.position[1]: #and map[self.position[0]][self.position[1]+1] == '.':
            
                new_position = (self.position[0], self.position [1]+1)

            
            self.position = new_position    #update monster position

            #print (f'MONSTER{Monster.data[0].position}')

            #else:
            
                #new_position=self.position


    
    def find_closest_player(self):


        distances = list()
        
        for player in Player.data:
        
            distance = abs(self.position[0] - player.position[0]) + abs(self.position[1] - player.position[1])
            
            distances.append(distance)

        shortest_distance = min(distances)

        for distance in distances:

            if distance == shortest_distance:

                return Player.data[distances.index(distance)]


