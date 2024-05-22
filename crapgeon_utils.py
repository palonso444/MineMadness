
import random
from collections import deque


#define a random location in map

def location(map:list[list[str]]) -> tuple[int]:
	
	height = random.randint(0,len(map)-1)
	
	width = random.randint(0,len(map[0])-1)
	
	return height, width


def check_for_free_spots(map:list[list[str]]) -> bool:

	for y in range (len(map)):
			
			for x in range(len(map[y])):
				
				if map[y][x] == '.':

					return True
	
	return False


def are_nearby (item1:object, item2:object) -> bool:	#check if two positions are nearby

	directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

	for direction in directions:
		
		row, col = item1.position[0] + direction[0], item1.position[1] + direction[1]
		
		if (row,col) == item2.position:
			
			return True
		
	return False
		

def get_distance(position1:tuple[int], position2:tuple[int]) -> int:

        return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])


def get_max_possible_distance(map:list[list[str]], position:tuple[int]) -> int:

	max_distance = get_distance(position, (0,0))

	if get_distance(position, (0,len(map[0])-1)) > max_distance:

		max_distance = get_distance(position, (0,len(map[0])-1))

	if get_distance(position, (len(map)-1,0)) > max_distance:

		max_distance = get_distance(position, (len(map)-1,0))

	if get_distance(position, (len(map)-1,len(map[0])-1)) > max_distance:

		max_distance = get_distance(position, (len(map)-1,len(map[0])-1))

	return max_distance


def check_within_limits(map:list[list[str]], position:tuple[int]) -> bool:

	if 0 <= position[0] <len(map) and 0 <= position[1] <len (map[position[0]]):
		return True
	return False


	



#creates map surface

def create_map (height:int, width:int) -> list[list[str]]:

	map = list()

	for y in range (height):

		map_width = list()

		for x in range (width):

			map_width.append('.')

		map.append(map_width)

	return map


#################################################  PLACING ITEMS AND CHARACTERS ON MAP  ###########################################


#place items on map in an exact way. Pass number of items to be placed. If a single item, position may be also passed as (y,x)
#If more than one item is placed and position is passed, from second item on they will be placed ramdonly
#Items do not overwrite each other. If given positions are occupied, item is placed somewhere else.

def place_equal_items(map:list[list[str]], item:str, number_of_items = 1, position = None) -> tuple[int]:

	for number in range (number_of_items):

		while check_for_free_spots(map):

			if not position or map [position[0]][position[1]] != '.':	# if position is taken, generates random location

				position = location (map)

			if map [position[0]][position[1]] == '.':

				map [position[0]][position[1]] = item

				if number_of_items == 1:
					return  (position[0],position[1])
				else:
					break



#place items on map in an approximate way. Pass frequency value from 0 (no items) to 1 (map full of items).
#If place position are occupied, new item overwrites placed item unless placed item is passed as 'protected'. Default: player, exit and coins.

def place_items (map:list[list[str]], item:str, frequency = 0.1, protected = None) -> None:

	number_of_items = (len(map)* len (map[0])) * frequency

	for number in range (int(number_of_items)):
			
		position = location (map)

		if not protected or map [position[0]][position[1]] not in protected:
		
			map [position[0]][position[1]] = item


#Returns 1 to 4 nearby positions regardless if occupied or not
def get_nearby_positions(map:list[list[str]],position:tuple[int], max_number = 4) -> set[tuple[int]]:

	nearby_positions = set()
	
	directions = ((0,1),(0,-1), (1,0), (-1,0))
	
	number = 0

	if check_within_limits(map, position):
	
		for direction in directions:

			if 0 <= position[0]+direction[0] < len(map) and (0 <= position[1]+direction[1] 
													< len(map[position[0]+direction[0]])):
				
				nearby_positions.add((position[0]+direction[0],position[1]+direction[1]))
				number += 1
		
			if number == max_number or directions.index(direction) == len(directions)-1:
				return nearby_positions
			
	

def place_items_as_group(map:list[list[str]], items:tuple[str], 
					   min_dist:int, max_dist:int|None = None, position:tuple[int]|None = None):


	items = deque(items)

	initial_position = place_equal_items(map, items.popleft(), position = position)

	placed_positions = [initial_position]
	tested_positions = {initial_position}

	item_to_place = items.popleft() if len(items)>0 else None
	map_area = len(map)*len(map[0])
	max_dist = min_dist if max_dist is None or max_dist < min_dist else max_dist
	
	while len(tested_positions) < map_area and item_to_place is not None:

		while True:
			cand_position = location(map)

			if cand_position not in tested_positions:
				tested_positions.add(cand_position)
				break
		
		max_dist_ok = False
		
		i = 0
		while i < len(placed_positions):
				
			if get_distance(cand_position,placed_positions[i]) < min_dist:
				break
			if get_distance(cand_position,placed_positions[i]) <= max_dist:
				max_dist_ok = True
				
			if i == len(placed_positions) - 1 and max_dist_ok:
				placed_positions.append(cand_position)
				place_equal_items(map, item_to_place, position=cand_position)
				item_to_place = items.popleft() if len(items)> 0 else None
			
			i += 1

		if len(tested_positions) == map_area and item_to_place is not None:
			tested_positions = set(placed_positions)





'''map = create_map(5,5)

map = [['#','#','#','#','#'],
	   ['#','.','#','#','#'],
	   ['.','#','#','#','#'],
	   ['#','#','#','#','#'],
	   ['#','#','#','#','#']]

place_items_as_group(map, ('U','y','r','U','y','r'), min_dist = 2, max_dist = 3)

for line in range(len(map)):
	print (*map[line])'''
