

class Character:

    blueprint_ids = ['%', 'M']
    
    def __init__(self, position, speed):    #position as [y,x]
        
        self.position = position
        self.speed = speed



class Player(Character):

    players = list ()
    blueprint_ids = ['%']

    def __init__(self, position, speed):
        super().__init__(position, speed)



class Monster(Character):

    monsters = list()
    blueprint_ids = ['M']

    def __init__(self, position, speed):
        super().__init__(position, speed)


