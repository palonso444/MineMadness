from kivy.uix.button import Button  # type: ignore
from kivy.animation import Animation
from kivy.properties import Clock
from kivy.graphics import Ellipse, Color

import crapgeon_utils as utils
import character_classes as characters
import token_classes as tokens


class Tile(Button):

    def __init__(self, row, col, kind, dungeon_instance, **kwargs):
        super().__init__(**kwargs)

        self.row = row
        self.col = col
        self.position = (row,col)
        self.kind = kind
        self.token = None   #defined later when token is placed on tile by DungeonLayout.place_tokens
        self.monster_token = None  #tiles can have up to 2 tokens (shovel + monster for instance). Special slot reserved for monsters in such cases
        self.damage_token = None
        self.dungeon = dungeon_instance     #need to pass the instance of the dungeon in order to cal dungeon.move_token from this class


    def on_release(self):

        player = self.dungeon.game.active_character

        if self.has_token('wall'):
            
            player.drill()

            self.clear_token()

            self.dungeon.game.update_switch('character_done')
            
            #self.dungeon.game.continue_turn()

        elif self.has_token('monster'):

            player.attack(self.get_character())

            self.clear_token()

            self.dungeon.game.update_switch('character_done')

            #self.dungeon.game.continue_turn()

        else:
        
            start_tile = self.dungeon.get_tile(player.position)

            start_tile.token.move_player(start_tile, self)
            
      
    def on_pos(self, *args):

        
        if self.token:
        
            self.token.pos = self.pos
            self.token.size = self.size


    def is_activable(self):
            
        player = self.dungeon.game.active_character
        
        path = self.dungeon.find_shortest_path(self.dungeon.get_tile(player.position), self, (player.blocked_by))

        if isinstance(self.token, tokens.CharacterToken) and self.token.character == player:

            return True
        
        if self.has_token('wall') and utils.are_nearby(self, player):
            
            if player.shovels > 0 or isinstance(player, characters.Hawkins):

                return True
            return False
            
        if self.has_token('monster') and utils.are_nearby(self, player):
            
            if player.weapons > 0 or isinstance(player, characters.CrusherJoe):

                return True
            return False
        
        if path and len(path) <= player.remaining_moves:

            return True
        
        return False
    

    def has_token(self, token_kind):

        if self.monster_token and self.monster_token.kind == token_kind:
            return True
        
        if self.token and self.token.kind == token_kind:
            return True
        
        return False


    def clear_token(self):
        

        if self.monster_token:
            self.dungeon.canvas.remove(self.monster_token)
            self.monster_token = None
        
        else:
            self.dungeon.canvas.remove(self.token)
            self.token = None
        

    def get_character(self):
        
        if self.monster_token:
            return self.monster_token.character
        else:
            return self.token.character