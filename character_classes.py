from random import randint


class Character:
    
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
    #Leader. Has a bit of all.

    def __init__(self):
        self.blocked_by = ('wall', 'monster')
        self.health = 3
        self.moves = 15
        self.shovels = 2
        self.weapons = 2
        self.gems = 0


class CrusherJoe(Player):
    pass
    #fighting arquetipe


class Hawkins (Player):
    pass
    #inventor. Drilling arquetype



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

    
    def find_closest_reachable_player(self):

        players_and_paths = list()

        start = self.dungeon.get_tile(self.position)
        
        for player in Player.data:

            goal = self.dungeon.get_tile(player.position)

            path = self.dungeon.find_shortest_path(start, goal, self.blocked_by)

            players_and_paths.append((player,path))

        
        closest_player = None
        
        for player_path in players_and_paths:

            if player_path[1]:

                if not closest_player or len(closest_player[1]) > len(player_path[1]):

                    closest_player = player_path

        
        return player_path


    def assess_path_smart(self):

        '''target = self.find_closest_reachable_player()[0] #REDO SO IT CAN TARGET ALSO GEMS, FOR INSTANCE
        target_tile = self.dungeon.get_tile(target.position)
        
        paths = list()
        
        #scanned = self.dungeon.scan(self.cannot_share_tile_with, exclude = True)   #look for free tiles in all dungeon

        scanned = self.dungeon.scan(scenery = (), exclude = True)

        
        #FIND PATHS FROM PLAYER TO ALL FREE TILES AND MAKE A LIST OF PATHS
        for position in scanned:

            scanned_tile = self.dungeon.get_tile(position)
            path = self.dungeon.find_shortest_path(target_tile, scanned_tile, self.blocked_by)

            if path:
                paths.append(path)


        #FIND SHORTEST PATH LENGTH IN LIST
        shortest_path_length = None

        for path in paths:

            if not shortest_path_length or len(path) < shortest_path_length:
                shortest_path_length = len(path)


        shortest_paths = list()
        
        for path in paths:

            if len(path) == shortest_path_length:
                shortest_paths.append(path)


        possible_paths_to_player = list ()
        
        start = self.dungeon.get_tile(self.position)
        
        for path in shortest_paths:

            goal = self.dungeon.get_tile(path[-1])

            path = self.dungeon.find_shortest_path(start, goal, self.blocked_by)

            possible_paths_to_player.append(path)

        
        shortest_path = None

        for path in possible_paths_to_player:

            if not shortest_path or len(path) < len(shortest_path):
                shortest_path = path        
        
        
        shortest_path = self.trim_path(shortest_path)
'''
        
        path = self.find_closest_reachable_player()[1] #REDO SO IT CAN TARGET ALSO GEMS, FOR INSTANCE

        path = self.trim_path(path)
        
        while len(path) > self.moves:

            path.pop()

        return path


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

        #TODO: if trim_path returns nothing (e.g. all path is occupied by fellow monsters)
        #the monster should move to the other directions towards the player, if possible

        return path
    

    def assess_path_random(self):

        path = list()

        position = self.position
        
        for move in range (self.moves):
        
            trigger = randint(1,10)

            if trigger <= self.motility:

                direction = randint(1,4) #1: NORTH, 2: EAST, 3: SOUTH, 4: WEST

                if direction == 1 and self.goes_through(self.dungeon.get_tile((position[0] -1, position[1]))):
                    
                        position = (position[0] -1, position [1])
                        path.append(position)

                elif direction == 2 and self.goes_through(self.dungeon.get_tile((position[0], position[1] +1))):
                    
                        position = (position[0], position[1]+1)
                        path.append(position)

                elif direction == 3 and self.goes_through(self.dungeon.get_tile((position[0] +1, position[1]))):
                    
                        position = (position[0] +1, position [1])
                        path.append(position)

                elif direction == 4 and self.goes_through(self.dungeon.get_tile((position[0], position[1] -1))):
                    
                        position = (position[0],position [1]-1)
                        path.append(position)


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

        if path:
        
            path = self.check_free_landing(path)
        
        if not path or len(path) == 0:
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
        self.motility = 8


    def move(self):

        return self.assess_path_direct()


class DepthsWisp(Monster):

    def __init__(self):
        self.moves = 3
        self.blocked_by = ()
        self.cannot_share_tile_with = ('monster', 'player')
        self.motility = 8


    def move(self):

        return self.assess_path_direct()
    

class RockElemental(Monster):
    pass

    #moves randomly and slowly but extremely strong if hits


class NightMare(Monster):
    
    def __init__(self):
        self.moves = 15
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')
        self.motility = None


    def move(self):

        return self.assess_path_smart()


class DarkDwarf(Monster):
    pass

    #chases the player. Intermediate strength


class MetalEater(Monster):
    pass

    #chases weapons and shovels and makes disappear. Does not attach player.


class GreedyGnome(Monster):
    pass

    #chases the nearest gold and stays on top of it. Intermediate strength