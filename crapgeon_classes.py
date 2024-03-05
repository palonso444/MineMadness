

class Character:

    blueprint_ids = ['%', 'M']
    
    def __init__(self, position, moves):    #position as tuple (y,x)
        
        self.position = position
        self.moves = moves


    def get_movement_range(self, dungeon_layout):

        
        mov_range = set()  #set of tuples (no repeated values)
        remaining_moves = self.moves
        
        # GET CURRENT PLAYER POSITION
        mov_range.add((self.position[0], self.position[1]))
        

        for move in range (1, remaining_moves + 1):     #starts at 1 not to include current player position again

            #INCLUDE ALL POSSIBLE MOVES ON THE SAME ROW AS PLAYER
            self.get_lateral_range(self.position[0], move, mov_range, dungeon_layout)

            if self.position[0] - move >= 0 or self.position[0] + move < dungeon_layout.rows: # if height within range up and down
            
            #INCLUDE ALL POSSIBLE MOVES SAME COLUMN AS PLAYER, DIRECTION UP
                mov_range.add((self.position[0] - move, self.position[1]))   #one step up.
            
            #INCLUDE ALL POSSIBLE MOVES SAME COLUMN AS PLAYER, DIRECTION DOWN
                mov_range.add((self.position[0] + move, self.position[1]))   #one step down.
                
                remaining_moves -= 1

            #INCLUDE ALL LATERAL MOVEMENTS STARTING FROM THE VERTICAL ARMS OF THE CROSS
                for side_move in range(1, remaining_moves + 1):

                    self.get_lateral_range(self.position[0] - move, side_move, mov_range, dungeon_layout)

                    self.get_lateral_range(self.position[0] + move, side_move, mov_range, dungeon_layout)
  
        return mov_range


    
    def get_lateral_range(self, y_position, side_move, mov_range, dungeon_layout):

            
            if self.position[1] - side_move >= 0: #if room in left side

                mov_range.add((y_position, self.position [1] - side_move)) #one step left.

            
            if self.position[1] + side_move < dungeon_layout.cols: #if room in right side             

                mov_range.add((y_position, self.position [1] + side_move)) #one step right



class Player(Character):

    players = list ()
    blueprint_ids = ['%']

    def __init__(self, position, moves):
        super().__init__(position, moves)




class Monster(Character):

    monsters = list()
    blueprint_ids = ['M']

    def __init__(self, position, moves):
        super().__init__(position, moves)


