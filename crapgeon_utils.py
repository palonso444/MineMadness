

import random


#define a random location in map

def location(map):
	
	height = random.randint(0,len(map)-1)
	
	width = random.randint(0,len(map[0])-1)
	
	location = [height, width]
	
	return location



def check_for_free_spots(map):

	for y in range (len(map)):
			
			for x in range(len(map[y])):
				
				if map[y][x] == '.':

					return True
	
	return False



#create map surface

def create_map (height, width):

	map = list()

	for y in range (height):

		map_width = list()

		for x in range (width):

			map_width.append('.')

		map.append (map_width)

	return map


#################################################  PLACING ITEMS AND CHARACTERS ON MAP  ###########################################


#place items on map in an exact way. Pass number of items to be placed. If a single item, coordinates may be also passed as (y,x)
#If more than one item is placed and coordinates are passed, from second item on they will be placed ramdonly
#Items do not overwrite each other in any case. If given coords are occupied, item is placed somewhere else.

def place_single_items(map, item, number_of_items = 1, coord = None):

	for number in range (int(number_of_items)):

		while check_for_free_spots(map):

			if not coord or map [coord[0]][coord[1]] != '.':	# if coordinades given point to a occupied spot, random location is passed

				coord = location (map)

			if map [coord[0]][coord[1]] == '.':

				map [coord[0]][coord[1]] = item

				break



#place items on map in an approximate way. Pass frequency value from 0 (no items) to 1 (map full of items).
#If place coord are occupied, new item overwrites placed item unless placed item is passed as 'protected'. Default: player, exit and coins.

def place_items (map, item, frequency = 0.1, protected = ['%', ' ', 'o']):

	number_of_items = (len(map)* len (map[0])) * frequency

	for number in range (int(number_of_items)):
			
		coord = location (map)

		if map [coord[0]][coord[1]] not in protected:
		
			map [coord[0]][coord[1]] = item


'''
#game setup

map = create_map(2,2)
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
'''