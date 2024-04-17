from random import randint


class Character:

    blueprint_ids = ('%', 'K', 'H', 'W')
    
    def __init__(self):    #position as tuple (y,x)
        
        self.position = None
        self.token = None
        self.dungeon = None
        self.id = None

    
    def update_position (self, y_position, x_position):

        self.__class__.data[self.id].position = (y_position, x_position)
        self.__class__.data[self.id].token.position = (y_position, x_position)

    
    def rearrange_ids (self):

        for character in self.__class__.data:

            if character.id > self.id:

                character.id -= 1


class Player(Character):

    data = list ()

    def __init__(self):

        self.remaining_moves = 0
    
    
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


class Vane(Player):

    def __init__(self):
        self.health = 3
        self.moves = 4
        self.shovels = 2
        self.weapons = 2
        self.gems = 0


class Monster(Character):

    data = list()

    def __init__(self):
        self.kind = 'monster'

    
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
        
        for move in range (self.moves):

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
        
        path = self.trim_path(path)

        return path
    

    def assess_path_random(self):

        path = list()

        position = self.position
        
        for move in range (self.moves):
        
            trigger = randint(1,10)

            if trigger <= self.motility:

                direction = randint(1,4) #1: NORTH, 2: EAST, 3: SOUTH, 4: WEST

                if direction == 1:

                    if self.goes_through(self.dungeon.get_tile((position[0] -1, position[1]))):
                    
                        position = (position[0] -1, position [1])
                        path.append(position)

                    else:
                        move -=1

                elif direction == 2:
                    
                    if self.goes_through(self.dungeon.get_tile((position[0], position[1] +1))):
                    
                        position = (position[0], position[1]+1)
                        path.append(position)

                    else:
                        move -=1

                elif direction == 3:
                    
                    if self.goes_through(self.dungeon.get_tile((position[0] +1, position[1]))):
                    
                        position = (position[0] +1, position [1])
                        path.append(position)

                    else:
                        move -=1

                elif direction == 4:
                    
                    if self.goes_through(self.dungeon.get_tile((position[0], position[1] -1))):
                    
                        position = (position[0],position [1]-1)
                        path.append(position)

                    else:
                        move -=1

        path = self.trim_path(path)

        return path
    

    def goes_through(self, tile):

        if tile:
        
            if tile.token and tile.token.kind in self.blocked_by:
                return False
            if tile.monster_token and tile.monster_token.kind in self.blocked_by:
                return False
               
            return True
        
        return False
    
    
    def check_free_landing(self, path):

        
        for position in reversed(path):
        
            for token_kind in self.cannot_share_tile_with:
        
                if len(path)>0 and self.dungeon.get_tile(path[-1]).has_token(token_kind):

                        path.remove(position)

        return path
    

    def trim_path(self, path):

        path = self.check_free_landing(path)
        
        if len(path) == 0:
            path = [self.position]

        return path
    


class Kobold(Monster):
    
    def __init__(self):
        self.moves = 4
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')
        self.motility = 8     #from 1 to 10. Rellevant in monsters with random movement


    def move(self):

        return self.assess_path_random()


class HellHound(Monster):
    
    def __init__(self):
        self.moves = 5
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')


    def move(self):

        return self.assess_path_direct()


class DepthsWisp(Monster):

    def __init__(self):
        self.moves = 3
        self.blocked_by = ()
        self.cannot_share_tile_with = ('monster', 'player')


    def move(self):

        return self.assess_path_direct()
    

class RockElemental(Monster):
    pass

    #moves randomly and slowly but extremely strong if hits


class NightMare(Monster):
    pass

    #chases the player. Fast and strong


class GreedyGnome(Monster):
    pass

    #chases the nearest gold and stays on top of it. Intermediate strength


class DarkDwarf(Monster):
    pass

    #chases the player. Intermediate strength