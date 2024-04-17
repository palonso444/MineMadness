

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


def are_nearby (item1, item2):	#check if two positions are nearby

	directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

	for direction in directions:
		
		row, col = item1.position[0] + direction[0], item1.position[1] + direction[1]
		
		if (row,col) == item2.position:
			
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

def place_items (map, item, frequency = 0.1, protected = ('%', ' ', 'o', 'W', 'K', 'H')): #REMOVE WKH

	number_of_items = (len(map)* len (map[0])) * frequency

	for number in range (int(number_of_items)):
			
		coord = location (map)

		if map [coord[0]][coord[1]] not in protected:
		
			map [coord[0]][coord[1]] = item