from kivy.uix.button import Button  # type: ignore

import crapgeon_utils as utils
import character_classes as characters


class Tile(Button):

    
    def __init__(self, row, col, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.row = row
        self.col = col
        self.position = (row,col)
        self.kind = kind
        self.token = None   #defined later when token is placed on tile by DungeonLayout.place_tokens
        self.monster_token = None  #tiles can have up to 2 tokens (shovel + monster for instance). Special slot reserved for monsters in such cases
        self.dungeon = dungeon_instance     #need to pass the instance of the dungeon in order to cal dungeon.move_token from this class


    def on_release(self):

        active_character = self.dungeon.game.active_character    

        if self.has_token('wall') or self.has_token('monster'):

            self.clear_token(active_character)

        else:

            start_position = (active_character.position[0], active_character.position[1])
        
            start_tile = self.dungeon.get_tile(start_position)

            start_tile.token.move_player(start_tile, self)
            
      
    def on_pos(self, *args):

        
        if self.token:
        
            self.token.pos = self.pos
            self.token.size = self.size


    def is_activable(self):
            
        player = self.dungeon.game.active_character
        
        path = self.dungeon.find_shortest_path(self.dungeon.get_tile(player.position), self, ('wall', 'monster'))

        if self.has_token('player'):

            return True
        
        if self.has_token('wall') and utils.are_nearby(self, player) and player.shovels > 0:

            return True
            
        if self.has_token('monster') and utils.are_nearby(self, player) and player.weapons > 0:

            return True
        
        if path and len(path) <= player.remaining_moves:  #if tile is reachable 

            return True
        
        return False
    

    def has_token(self, token_kind):

        if self.monster_token and self.monster_token.kind == token_kind:
            return True
        
        if self.token and self.token.kind == token_kind:
            return True
        
        return False


    def clear_token(self, active_character):
        
        def remove_token():
            if self.monster_token:
                self.dungeon.canvas.remove(self.monster_token)
                self.monster_token = None
            else:
                self.dungeon.canvas.remove(self.token)
                self.token = None
        

        if self.has_token('monster'):

            if self.monster_token:
                token = self.monster_token
            else:
                token = self.token

            active_character.weapons -= 1
            active_character.remaining_moves -=1
            self.dungeon.game.weapons = not self.dungeon.game.weapons   # triggers display of updated value
            token.character.rearrange_ids()
            characters.Monster.data.remove(token.character)

        elif self.has_token('shovel'):

            active_character.shovels += 1
            self.dungeon.game.shovels = not self.dungeon.game.shovels   # triggers display of updated value

        elif self.has_token('weapon'):

            active_character.weapons += 1
            self.dungeon.game.weapons = not self.dungeon.game.weapons   # triggers display of updated value

        elif self.has_token('wall'):

            active_character.shovels -= 1
            active_character.remaining_moves -=1
            self.dungeon.game.shovels = not self.dungeon.game.shovels   # triggers display of updated value

        elif self.has_token('gem'):

            active_character.gems +=1
            self.dungeon.game.gems = not self.dungeon.game.gems

        remove_token()