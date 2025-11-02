import random
import os 


#NOTE: add arrows (/). Shoot to one direction and kill first monster within a range


#define a random location in map

def location(map):
	
	height = random.randint(0,len(map)-1)
	width = random.randint(0,len(map[0])-1)
	location = [height, width]
	
	return location

	
#player inputs movement

def input_move():
	
	move = input('\nEnter move - E (up) / X (down) / S (left) / F (right) / T (wait) / P (drink potion):')
		
	while move.lower() not in ['e', 'x','s','f','t', 'p']:
		
		move = input('\nPlease enter a valid move (E/X/S/F/T/I/M/J/L):')
		
			
	return move.lower()
		
		
#create map

def create_map (width, height):
	
	map = list()
	
	for y in range (height):
	
			map_width = list()
			
			for x in range(width):
				map_width.append('.')
			
			map.append(map_width)
	
	return map
	

#define speed and killer attributes of class Monster

def define_monsters (speed = 1, killer = False):
	
	Monster.speed = speed
	Monster.killer = killer



#place walls. Introduce factor from 0 (no walls) to 10 (a lot of walls)

def place_walls(map, factor = 0):
	
	number_of_walls = (len(map) * len(map[0])) * factor * 0.1

	for x in range (int(number_of_walls)):
		coord = location (map)
		map[coord[0]][coord[1]] = '#'
		
	
#place exit

def place_exit(map):
	
	while True: #avoid placing exit on player
		coord= location(map)
		if map[coord[0]][coord[1]] != '%':
			map[coord[0]][coord[1]] = ' '
			break
	
	
	#if there is a monster in the spot where exit is placed, the monster must be removed from the database
	
	for monster in Monster.data:
		if monster.position[0] == coord[0] and monster.position[1] == coord [1]:
			Monster.data.remove(monster)


#place shovels

def place_shovels (map, factor = 0):
	
	number_of_shovels = (len(map) * len(map[0])) * factor * 0.001

	for x in range (int(number_of_shovels)):
		coord = location (map)
		map[coord[0]][coord[1]] = 'p'


#place_weapons

def place_weapons (map, factor = 0):
	
	number_of_weapons = (len(map) * len(map[0])) * factor * 0.001

	for x in range (int(number_of_weapons)):
		coord = location (map)
		map[coord[0]][coord[1]] = 'x'


#place coins

def place_coins(map, player, number = 0):
		
		coins = 0
	
		while coins < number:
			coord= location(map)
		
			if map [coord[0]][coord[1]] == '.':
			
				map [coord[0]][coord[1]] = 'o'
				coins += 1
				player.coins_obj += 1


#place speed potions

def place_potions(map, number = 0):
		
		potions = 0
	
		while potions < number:
			coord= location(map)
		
			if map [coord[0]][coord[1]] == '.':
			
				map [coord[0]][coord[1]] = 's'
				potions += 1
		

#place monsters

def place_monsters (map, number = 1):
	
	monster = 0
	
	while monster < (number):
		coord= location(map)
		
		if map [coord[0]][coord[1]] == '.':
			
			new_monster = Monster(coord[0], coord[1])
			Monster.data.append (new_monster)
			
			map [coord[0]][coord[1]] = 'M'
			monster += 1


#print game interface	
			
def print_map(map, player):
	
	os.system('clear') #clears screen
	
	for y in range (len(map)):
		print (' '.join(map[y]))
		
	print(f'\nWeapons: {player.weapon}')
	print(f'Shovels: {player.digging}')
	print(f'Potions: {player.potions}')
	print(f'Coins: {player.coins} / {player.coins_obj}')
	print('\nCollect all coins before escaping!')


#check if cornered

def corner_check(map, character, exits):
	
	surroundings = list()
	
	if character.position[1] != 0:
		surroundings.append (map[character.position[0]] [character.position[1]-1])
	
	if character.position[1] != len(map[0]) -1:
		surroundings.append (map[character.position[0]] [character.position[1]+1])
	
	if character.position[0] != 0:
		surroundings.append (map[character.position[0]-1] [character.position[1]])
	
	if character.position[0] != len(map)-1:	
		surroundings.append (map[character.position[0]+1] [character.position[1]])
	
	if 'M' not in surroundings:
		return False
	
	elif not Monster.killer:
		for char in surroundings:
			if char in exits:
				return False
		
	return True


# class monster is called by place_monsters

class Monster:
	
	data = list()
	#killer and speed defined by define_monsters()
	
	def __init__(self, height, width):
		self.position = [height, width]
	
	
	def move(self, map):	
			
		if player.position[0] < self.position[0] and map[self.position[0]-1] [self.position[1]] == '.':
				
			new_position = [self.position[0] -1, self.position [1]]	
				
		elif player.position[0] > self.position[0] and (map[self.position[0] +1][self.position[1]] == '.'):
					
			new_position = [self.position[0] +1, self.position [1]]
				
		elif player.position[1] < self.position[1] and map[self.position[0]][self.position[1] -1] == '.':
			
			new_position = [self.position[0],self.position [1]-1]
				
		elif player.position[1] > self.position[1] and map[self.position[0]][self.position[1]+1] == '.':
			
			new_position = [self.position[0], self.position [1]+1]
				
		else:
				new_position=self.position
				
		map [self.position[0]] [self.position[1]] = '.'
		
		self.position = new_position
			
		map [self.position[0]] [self.position[1]] = 'M'



class Player:
		
	def __init__(self, speed = 2, weapon = 0, digging = 0, coins_obj = 0, potions = 0, arrows = 0, range = 3):
		self.speed = speed
		self.weapon = weapon
		self.digging = digging
		self.coins_obj = coins_obj
		self.coins = 0
		self.arrows = arrows
		self.range = range
		self.potions = potions
		
	
	def place (self, map, height = None, width = None):
	
		if height is None or width is None:
			height = location(map)[0]
			width = location(map)[1]
		
		map[height][width] = '%'
			
		self.position = [height, width] 
			
	
	def get_move (self, map, move):
		
		global shoot
		

		if move == 'e':
			new_position = [self.position[0] -1,self.position[1]]
			
		elif move == 'x':
			new_position = [self.position[0] +1,self.position[1]]
			
		elif move == 's':
			new_position = [self.position[0], self.position[1]-1]
			
		elif move == 'f':
			new_position = [self.position[0], self.position[1]+1]
			
		elif move == 't':
			new_position = self.position
			
		elif move in ['i', 'm','j','l']:
			new_position = self.position
			if self.arrows > 0:
				self.get_shot(move)
				
		elif move == 'p':
			new_position = self.position
			if self.potions > 0:
				global potion_drunk
				self.speed = 4
				self.potions -= 1
				potion_drunk = True
			
			
		return new_position
		
############################################### NOT IMPLEMENTED ##################################################################################		
	
	def get_shot(self, move):
		
		global shoot
		
		shoot = True
		
		
		if move == 'i':
				shot = (- self.range, 0)
			
		elif move == 'm':
				shot = (self.range, 0)
			
		elif move == 'j':
				shot = (0, - self.range)
			
		elif move == 'l':
				shot = (0, self.range)
			
		return shot
	
	
	def shoot_arrow(shot, map):
			
		global shoot
		
		shoot = False
		
		self.arrows -= 1
			
#######################################################################################################################################################		
		

		#check if new position is exists and is free
		
	def move_check (self, map, new_position):
		
		global victory
		
		#ouside map up or down	
		if new_position[0] == -1 or new_position[0] == len(map):
			
			new_position = self.position
		
		#outside map left or right
		elif new_position[1] == -1 or new_position[1] == len(map[0]):
		
			new_position = self.position
			
		#new position is exit. Victory!
		elif map[new_position[0]][new_position [1]] == ' ' and player.coins >= player.coins_obj:
			
			victory = True	
		
		#take weapon
		elif map[new_position[0]][new_position [1]] == 'x':
			self.weapon += 1
			
		#take shovel
		elif map[new_position[0]][new_position [1]] == 'p':
			self.digging += 1
			
		#take coin
		elif map[new_position[0]][new_position [1]] == 'o':
			self.coins+= 1
			
		#take speed potion	
		elif map[new_position[0]][new_position [1]] == 's':
			self.potions+= 1
							
		#dig 
		elif map[new_position[0]][new_position [1]] == '#' and self.digging > 0:
			
			map[new_position[0]][new_position [1]] = '.'
			self.digging -= 1
			new_position = self.position	
					
		#kill monster
		elif map[new_position[0]][new_position [1]] == 'M' and self.weapon > 0:
			
			map[new_position[0]][new_position [1]] = '.'
			self.weapon -= 1
			for monster in Monster.data:
				if monster.position[0] == new_position[0] and monster.position[1] == new_position [1]:
					Monster.data.remove(monster)
			new_position = self.position
			
		#new position occupied
		elif map[new_position[0]][new_position [1]] != '.':
			new_position = self.position
			
			
		return new_position
		
		
	def move(self, map, position):
		
		map [self.position[0]] [self.position[1]] = '.'
		self.position = position
			
		map [self.position[0]] [self.position[1]] = '%'
				

#game setup

map = create_map(15,15)
place_walls(map, 5)
place_weapons(map, 20)
place_shovels(map, 30)
player = Player(speed = 2, digging = 3, weapon = 3)
player.place(map, 0, 0)
define_monsters(speed=1, killer = True)
place_monsters(map, 12)
place_exit(map)
place_coins(map, player, 5)
place_potions(map, 3)

defeat = False
victory = False
shoot = False
potion_drunk = False

# game loop

while True:

	print_map (map, player)

	moves = 0
	
	while moves < player.speed:

		player_move = input_move()
			
		new_position = player.get_move(map, player_move)
		
		new_position = player.move_check(map, new_position)
		
		if shoot:
			
			player.shoot_arrow(shot, map)
			
		
		else:
		
			player.move (map, new_position)
			
		
		print_map (map, player)
		
		if victory:
			break
		
		moves += 1
		
		if potion_drunk:	# if potion was drunk moves are reset (you get as many free moves as the potion effect states)
			
			moves = 0
			potion_drunk = False
		
	if victory:
		break

	player.speed = 2		# resets player speed to default in case potion was drunk (effect is now over)
	
	for monster in Monster.data:
		for move in range(Monster.speed):
			monster.move(map)
			
	print_map(map, player)
	defeat = (corner_check(map, player,'.opxs '))
			
	if defeat:
		break

if victory:
		print ('\nYou escaped the dungeon!')
elif defeat:
		print('\nThe monsters got you!')
		
