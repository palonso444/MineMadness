from random import randint

import crapgeon_utils as utils
import token_classes as tokens


class Character:

    #TODO: make this funcitons work. Problem with "character.__class__.data":

    '''def rearrange_ids ():

        for character in character.__class__.data:

            character.id = character.__class__.data.index(character)
            
            
        def reset_moves():

            for character in character.__class__.data:
                character.remaining_moves = character.moves'''
    


    
    def __init__(self):    #position as tuple (y,x)
        
        self.position = None
        self.token = None
        self.dungeon = None
        self.id = None
        self.remaining_moves = 0

    
    def update_position (self, y_position, x_position):

        self.__class__.data[self.id].position = (y_position, x_position)
        self.__class__.data[self.id].token.position = (y_position, x_position)

    
    def rearrange_ids (self):

        for character in self.data:

            character.id = self.data.index(character)

    
    def attack (self, opponent):

        if isinstance(self, Player):
            if self.weapons > 0:
                self.weapons -=1
                self.dungeon.game.update_switch('weapons')

        damage = randint(self.strength[0], self.strength[1])
        opponent.health -= damage
        
        self.remaining_moves -= 1

        if opponent.health <= 0:
            opponent.data.remove(opponent)
            opponent.rearrange_ids()
        
        self.dungeon.show_damage_token (opponent.token.pos, opponent.token.size)


    def has_moved(self):

        if self.remaining_moves == self.moves:
            return False
        return True
    


class Player(Character):

    data = list ()

    def reset_moves():

        for player in Player.data:
            player.remaining_moves = player.moves


    def __init__(self):
        super().__init__()
        self.blocked_by = ('wall', 'monster')
        self.cannot_share_tile_with = ('wall', 'monster','player')
        self.shovels = 0
        self.weapons = 3
        self.gems = 0
    
    
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


    def pick_object(self, token_kind):

        
        character_attribute = getattr(self, token_kind + 's')
        character_attribute += 1
        setattr(self, token_kind + 's', character_attribute)

        self.dungeon.game.update_switch(token_kind + 's')


    def drill(self):

        self.shovels -= 1
        self.remaining_moves -=1
        self.dungeon.game.update_switch('shovels')


class Vane(Player):
    #Leader. More moves. picks gems. 

    def __init__(self):
        super().__init__()
        self.data = super().data
        self.health = 30
        self.strength = (1,1)
        self.moves = 2


class CrusherJoe(Player):
    #Fighter. Can attack with no weapons. Super strong if attack with weapons

    def __init__(self):
        super().__init__()
        self.data = super().data
        self.health = 3
        self.strength = (1,1)
        self.moves = 4


class Hawkins (Player):
    #Inventor. No need showels to drill. Low health. Cannot pick shovels
    
    def __init__(self):
        super().__init__()
        self.data = super().data
        self.health = 30
        self.strength = (1,1)
        self.moves = 2



class Monster(Character):

    data = list()

    def __init__(self):
        super().__init__()
        self.kind = 'monster'
        self.random_motility = 0

    def reset_moves():

        for monster in Monster.data:
            monster.remaining_moves = monster.moves
    
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

        
        closest_player_and_path = None
        
        for player_and_path in players_and_paths:

            if player_and_path[1]:

                if not closest_player_and_path or len(closest_player_and_path[1]) > len(player_and_path[1]):

                    closest_player_and_path = player_and_path

        return closest_player_and_path


    def find_accesses(self, target, smart = True):    #returns list of paths from target to free tiles, sorted shortest to longest

        target_tile = self.dungeon.get_tile(target.position)
        
        paths = list()
        
        #look which tiles are free in the dungeon
        scanned = self.dungeon.scan(self.cannot_share_tile_with, exclude = True)
        
        #find paths from player to all free tiles scanned
        for tile_position in scanned:

            scanned_tile = self.dungeon.get_tile(tile_position)
            
            if smart:   #smart creatures do not go to places where there is no direct path to player
                path = self.dungeon.find_shortest_path(target_tile, scanned_tile, self.blocked_by)

            else:
                path = self.dungeon.find_shortest_path(target_tile, scanned_tile)
            
            if path:

                paths.append(path)
        
        #sort paths from player to free tiles from shortest to longest
        sorted_paths = sorted(paths, key=len)

        return sorted_paths


    def assess_path_smart(self):
        
        target = self.find_closest_reachable_player()[0]

        target_tile = self.dungeon.get_tile(target.position)

        sorted_paths = self.find_accesses(target)

        shortest_possible_path = None
        
        for path in sorted_paths:
            #check if monster can reach end_tile of each of sorted paths
            possible_path = self.dungeon.find_shortest_path(self.token.start, self.dungeon.get_tile(path[-1]), self.blocked_by)

            if possible_path:
            
                monster_to_target = self.dungeon.find_shortest_path(self.token.start, target_tile, self.blocked_by)
                target_to_possible_path_end = self.dungeon.find_shortest_path(target_tile, self.dungeon.get_tile(possible_path[-1]), self.blocked_by)
                #if end tile closer to player than monster is right now, take path to this end tile
                if len(target_to_possible_path_end) < len(monster_to_target):

                    shortest_possible_path = possible_path
                    break

        path = self.trim_path(shortest_possible_path)

        return path


    def assess_path_direct(self):

        target = self.find_closest_reachable_player()[0] #REDO SO IT CAN TARGET ALSO GEMS, FOR INSTANCE

        sorted_paths = self.find_accesses(target, smart = False)

        path = None
        
        for sorted_path in sorted_paths:

            if path:
                break

            end_tile = self.dungeon.get_tile(sorted_path[-1])

            possible_path = self.dungeon.find_shortest_path(self.token.start, end_tile, self.blocked_by)

            if not possible_path:
                continue
            
            distance = utils.distance(self.position, target.position)
            
            for position in possible_path:

                if distance <= utils.distance(position, target.position):

                    break

                elif distance > utils.distance(position, target.position):

                    distance = utils.distance(position, target.position)

                if possible_path.index(position) == len(possible_path) -1:

                    path = possible_path
                        
        path = self.trim_path(path)
        
        return path
    

    def assess_path_random(self):

        path = list()

        position = self.position
        
        for move in range (self.moves):
        
            trigger = randint(1,10)

            if trigger <= self.random_motility:

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

            while len(path) > self.moves:
                path.pop()
        
            path = self.check_free_landing(path)
        
        if not path or len(path) == 0:
            path = [self.position]

        return path
    



class Kobold(Monster):
    
    def __init__(self):
        super().__init__()
        self.data = super().data
        self.moves = 4
        self.health = 1
        self.strength = (1,1)
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')
        self.random_motility = 8     #from 1 to 10. Rellevant in monsters with random movement


    def move(self):

        return self.assess_path_random()
    


class HellHound(Monster):
    
    def __init__(self):
        super().__init__()
        self.data = super().data
        self.moves = 5
        self.health = 1
        self.strength = (1,1)
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')
        self.random_motility = 8


    def move(self):

        if self.find_closest_reachable_player():

            return self.assess_path_direct()
        
        else:
            
            return self.assess_path_random()



class DepthsWisp(Monster):

    def __init__(self):
        super().__init__()
        self.data = super().data
        self.moves = 3
        self.health = 1
        self.strength = (1,1)
        self.blocked_by = ()
        self.cannot_share_tile_with = ('monster', 'player')
        self.random_motility = 8


    def move(self):

        return self.assess_path_direct()
    

class RockElemental(Monster):
    pass

    #moves randomly and slowly but extremely strong if hits


class NightMare(Monster):
    
    def __init__(self):
        super().__init__()
        self.data = super().data
        self.moves = 7
        self.health = 1
        self.strength = (1,1)
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')


    def move(self):

        if self.find_closest_reachable_player():

            return self.assess_path_smart()
        
        else:
            return [self.position]


class DarkDwarf(Monster):
    pass

    #chases the player. Intermediate strength


class MetalEater(Monster):
    pass

    #chases weapons and shovels and makes disappear. Does not attach player.


class GreedyGnome(Monster):
    pass

    #chases the nearest gold and stays on top of it. Intermediate strength