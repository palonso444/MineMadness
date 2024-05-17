from random import randint

import crapgeon_utils as utils
import token_classes as tokens
import tile_classes as tiles


class Character:

    #TODO: make this funcitons work. Problem with "character.__class__.data":

    '''def rearrange_ids ():

        for character in character.__class__.data:

            character.id = character.__class__.data.index(character)
            
            
        def reset_moves():

            for character in character.__class__.data:
                character.remaining_moves = character.moves'''
    


    
    def __init__(self):    #position as tuple (y,x)
        
        self.name = None
        self.position = None
        self.token = None
        self.dungeon = None
        self.id = None
        self.remaining_moves = 0

    
    def update_position (self, y_position, x_position):

        self.__class__.data[self.id].position = (y_position, x_position)

    
    def rearrange_ids (self):

        for character in self.data:

            character.id = self.data.index(character)

    
    def fight_on_tile (self, opponent_tile):

        opponent = opponent_tile.get_character()

        damage = randint(self.strength[0], self.strength[1])
        if isinstance(self, Player) and self.weapons > 0:
            self.weapons -= 1
            self.dungeon.game.update_switch('weapons')
            if self.armed_strength_incr:
                damage += self.armed_strength_incr
        
        opponent.health -= damage
        self.remaining_moves -= 1

        if opponent.health <= 0:
            opponent.data.remove(opponent)
            opponent.rearrange_ids()
            opponent_tile.clear_token(opponent.token.kind)
        
        self.dungeon.show_damage_token (opponent.token.shape.pos, opponent.token.shape.size)


    def has_moved(self):

        if self.remaining_moves == self.moves:
            return False
        return True
    


class Player(Character):

    player_chars = ('%', '?', '&')  # % sawyer, ? hawkins, & crusher jane
    data = list ()
    exited = set()
    gems = 0

    def transfer_player(name):
        
        for player in Player.exited:
            if player.name == name:
                return player

    def reset_moves():

        for player in Player.data:
            player.remaining_moves = player.moves


    def __init__(self):
        super().__init__()
        self.blocked_by = ('wall', 'monster')
        self.cannot_share_tile_with = ('wall', 'monster','player')
        self.free_actions = (None,)
        self.shovels = 0
        #self.moves = 3
        self.digging_moves = 1
        self.weapons = 0
        self.armed_strength_incr = None
        self.ignores = (None,)
    
    
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


    def pick_object(self, object_tile):

        if object_tile.token.species not in self.ignores:
            
            if object_tile.token.species == 'gem':

                Player.gems += 1
                self.dungeon.game.update_switch('gems')
            
            elif object_tile.token.species == 'jerky':

                self.health += 2
                self.health = self.max_health if self.health > self.max_health else self.health
                self.dungeon.game.update_switch('health')

            else:
                character_attribute = getattr(self, object_tile.token.species + 's')
                character_attribute += 1
                setattr(self, object_tile.token.species + 's', character_attribute)
                self.dungeon.game.update_switch(object_tile.token.species + 's')
            
            object_tile.clear_token(object_tile.token.kind)


    def dig(self, wall_tile):

        if self.shovels > 0:
            self.shovels -= 1
            self.dungeon.game.update_switch('shovels')
        self.remaining_moves -= self.digging_moves

        self.dungeon.show_digging_token(wall_tile.token.shape.pos, wall_tile.token.shape.size)

        wall_tile.clear_token('wall')
        
        


class Sawyer(Player):
    '''Slow digger (takes half of initial moves each dig)
        Can pick gems
        LOW strength
        LOW health
        HIGH movement''' 

    def __init__(self):
        super().__init__()
        self.data = super().data
        self.char = '%'
        self.name = 'Sawyer'
        self.health = 400
        self.max_health = self.health
        self.strength = (1,2)
        self.moves = 5
        self.digging_moves = 3


class CrusherJane(Player):
    '''Can fight with no weapons (MEDIUM strength)
        Stronger if fight with weapons  (HIGH strength)
        Cannot pick gems
        LOW movement
        '''

    def __init__(self):
        super().__init__()
        self.data = super().data
        self.name = 'Crusher Jane'
        self.char = '&'
        self.free_actions = ('fighting',)
        self.health = 8
        self.max_health = self.health
        self.strength = (3,6)
        self.armed_strength_incr = 2
        self.moves = 3
        self.ignores = ('gem',)


class Hawkins (Player):
    '''Can dig without shovels
    Does not pick shovels
    Can fight with weapons
    Cannot pick gems
    LOW health
    MEDIUM strength
    MEDIUM movement'''
    
    def __init__(self):
        super().__init__()
        self.data = super().data
        self.name = 'Hawkins'
        self.char = '?'
        self.free_actions = ('digging',)
        self.health = 5
        self.max_health = self.health
        self.strength = (1,4)
        self.moves = 4
        self.ignores = ('shovel', 'gem')



class Monster(Character):

    data = list()

    def __init__(self):
        super().__init__()
        self.kind = 'monster'
        self.random_motility = 0    #from 0 to 10. Rellevant in monsters with random movement
        self.ignores = ('shovel', 'weapon', 'gem', 'jerky')
        self.attacks = 2

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

    
    def find_closest_reachable_target(self, target_kind:str, target_species:str|None = None) -> tiles.Tile|None:

        '''
        Finds closest target based on len(path) and returns the tile where this target is placed
        Returns tile is there is path to tile, None if tile is unreachable"
        '''

        tiles_and_paths = list()
        start_tile = self.dungeon.get_tile(self.position)
        
        for tile in self.dungeon.children:

            if tile.has_token_kind(target_kind):

                if target_species is None or tile.second_token.species == target_species or (tile.token.species 
                                                                                             == target_species):

                    path = self.dungeon.find_shortest_path(start_tile, tile, self.blocked_by)
                    tiles_and_paths.append((tile,path))

        
        closest_tile_and_path = None
        
        for tile_and_path in tiles_and_paths:

            if tile_and_path[1] is not None: # if path is not None

                if closest_tile_and_path is None or len(closest_tile_and_path[1]) > len(tile_and_path[1]):

                    closest_tile_and_path = tile_and_path

        return closest_tile_and_path if closest_tile_and_path is None else closest_tile_and_path[0]


    def find_accesses(self, target_tile, smart = True):    #returns list of paths from target to free tiles, sorted shortest to longest
        '''
        Returns a list of paths, sorted from shorter to longer,
        from target to all free tiles in the dungeon
        path[-1] is position of free tile in the dungeon, path[0] is position nearby to target_tile
        '''

        paths = list()
        
        #look which tile positions are free in the dungeon among ALL tiles
        scanned = self.dungeon.scan(self.cannot_share_tile_with, exclude = True)
        
        #find paths from target_tile to all free tiles scanned
        for tile_position in scanned:

            scanned_tile = self.dungeon.get_tile(tile_position)
            
            if smart:   #smart creatures avoid tiles where, althogh closer in position, the path to target is longer
                path = self.dungeon.find_shortest_path(target_tile, scanned_tile, self.blocked_by)

            else:
                path = self.dungeon.find_shortest_path(target_tile, scanned_tile)
            
            if path:

                paths.append(path)
        
        #sort paths from player to free tiles from shortest to longest
        
        sorted_paths = sorted(paths, key=len)

        return sorted_paths


    def assess_path_smart(self, target_tile):

        accesses = self.find_accesses(target_tile)
        #print (accesses, '\n')
        
        i = 0
        while i < len(accesses):
            
            #if access is unreachable, remove access
            path_access_end = self.dungeon.find_shortest_path(self.token.start, self.dungeon.get_tile(accesses[i][-1]), self.blocked_by)
            if path_access_end is None:
                accesses.remove(accesses[i])
                i -=1
                
                #print (accesses, '\n')

            #remove all accesses longer than first access (the shortest)
            if len(accesses[i]) > len(accesses[0]):
                accesses.remove(accesses[i])
                i -=1
                
                #print('ONLY SHORTEST REMAIN')
                #print (accesses, '\n')

            
            #if access end further away from target than monster is, remove access
            else:
                monster_to_target = self.dungeon.find_shortest_path(self.token.start, 
                                                                    target_tile, self.blocked_by)
                target_to_access_end = self.dungeon.find_shortest_path(target_tile, 
                                                                       self.dungeon.get_tile(accesses[i][-1]), self.blocked_by)
                
                if len(target_to_access_end) > len(monster_to_target):
                    accesses.remove(accesses[i])
                    i -=1
            #print (accesses, '\n')

            i += 1

        path_to_closest_access = None

        for access in accesses:

            end_tile = self.dungeon.get_tile(access[-1])
            path_to_access = self.dungeon.find_shortest_path(self.token.start, end_tile, self.blocked_by)
            if path_to_access is not None:
                if path_to_closest_access is None or len(path_to_closest_access) > len(path_to_access):
                    path_to_closest_access = path_to_access

        path = self.trim_path(path_to_closest_access)

        return path


    def assess_path_direct(self, target_tile):

        sorted_paths = self.find_accesses(target_tile, smart = False)

        path = None
        
        for sorted_path in sorted_paths:

            if path:
                break

            end_tile = self.dungeon.get_tile(sorted_path[-1])

            possible_path = self.dungeon.find_shortest_path(self.token.start, end_tile, self.blocked_by)

            if not possible_path:
                continue
            
            distance = utils.get_distance(self.position, target_tile.position)
            
            for position in possible_path:

                if distance <= utils.get_distance(position, target_tile.position):

                    break

                elif distance > utils.get_distance(position, target_tile.position):

                    distance = utils.get_distance(position, target_tile.position)

                if possible_path.index(position) == len(possible_path) -1:

                    path = possible_path
                        
        path = self.trim_path(path)
        
        return path
    

    def assess_path_random(self):

        path = list()

        position = self.position
        
        for move in range(self.moves):
        
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
    

    def attack_players(self):

        players = Player.data[:]
        
        for player in players:
            if utils.are_nearby(self, player) and self.remaining_moves > 0:

                player_tile = self.dungeon.get_tile(player.position)
                self.fight_on_tile(player_tile)


    def goes_through(self, tile):

        if tile:
        
            if tile.token and tile.token.kind in self.blocked_by:
                return False
            if tile.second_token and tile.second_token.kind in self.blocked_by:
                return False
               
            return True
        
        return False
    
    
    def check_free_landing(self, path):

        
        for position in reversed(path):

            if path.index(position) != len(path)-1:  
                break   #at this stage only last position in path is rellevant
        
            for token_kind in self.cannot_share_tile_with:
                
                #position != self.position is necessary for random moves
                if self.dungeon.get_tile(position).has_token_kind(token_kind) and position != self.position:
                        
                    path.remove(position)
        
        return path
    

    def trim_path(self, path):

        if path:

            while len(path) > self.moves:
                path.pop()
        
            path = self.check_free_landing(path)
        
        if not path or len(path) == 0:
            path = None

        return path
    



class Kobold(Monster):
    
    def __init__(self):
        super().__init__()
        self.data = super().data
        self.name = 'Kobold'
        self.moves = 3
        self.health = 2
        self.max_health = self.health
        self.strength = (1,2)
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')
        self.random_motility = 8


    def move(self):

        return self.assess_path_random()
    


class CaveHound(Monster):
    
    def __init__(self):
        super().__init__()
        self.data = super().data
        self.name = 'Cave Hound'
        self.moves = 4
        self.health = 4
        self.max_health = self.health
        self.strength = (1,4)
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')
        self.random_motility = 8


    def move(self):

        target_tile = self.find_closest_reachable_target('player')

        if target_tile is not None:
            return self.assess_path_direct(target_tile)
        
        else:
            return self.assess_path_random()



class DepthsWisp(Monster):

    def __init__(self):
        super().__init__()
        self.data = super().data
        self.name = 'Depths Wisp'
        self.moves = 5
        self.health = 1
        self.max_health = self.health
        self.strength = (1,2)
        self.blocked_by = ()
        self.cannot_share_tile_with = ('monster', 'player')
        self.ignores = self.ignores + ('rock',)
        self.random_motility = 5


    def move(self):

        if self.find_closest_reachable_player():

            return self.assess_path_direct()
        
        else:
            
            return self.assess_path_random()
    

class RockElemental(Monster):
    pass

    #moves randomly and slowly but extremely strong if hits


class NightMare(Monster):
    
    def __init__(self):
        super().__init__()
        self.data = super().data
        self.name = 'Nightmare'
        self.moves = 40
        self.health = 6
        self.max_health = self.health
        self.strength = (2,5)
        self.blocked_by = ('wall', 'player')
        self.cannot_share_tile_with = ('wall', 'monster', 'player')


    def move(self):

        target_tile = self.find_closest_reachable_target('player')
        
        if target_tile is not None:

            return self.assess_path_smart(target_tile)
        
        else:
            return None


class DarkDwarf(Monster):
    pass

    #chases the player. Intermediate strength


class MetalEater(Monster):
    pass

    #chases weapons and shovels and makes disappear. Does not attack player.


class GreedyGnome(Monster):
    pass

    #chases the nearest gold and stays on top of it. Intermediate strength