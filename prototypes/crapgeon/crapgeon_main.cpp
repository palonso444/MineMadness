

//reference to header file. All others includes are here.
#include "crapgeon_utils.h"


int main () {
	
	
	bool player_alive = true;
	
	srand(time(NULL));
		
	
	//starting room
	
	Room current_room (20,20, "N");
	
	Room::room_database_add (current_room);
		
	
	// create and put player in starting room
	
	Character character1;
	
	character1.position_character (13,13, current_room);
	
		
	do {
	
	
		std::string exit;
			
	
		do {	// move player inside room. input_movement returns "V" if player stays in room
		
			
			current_room.print_room ();
			
			exit = character1.input_movement (current_room);
			
			clrscr();
					 
 	
		}
	
		while (exit == "V");
			
		
		if (current_room.door_was_crossed (exit)) {	// player went to previously visited room
			
			// gets adjacent room from database according to direction taken by player
			// adjacent room_identifier = current_room.adjacent_room_get (exit)	
			Room new_room = Room::room_database_get(current_room.adjacent_room_get (exit));		
			
			current_room = new_room;		
		
		}
		
		else {	// player goes to new room.  
		
		
		
			//creates new room, adds current room as adjacent, adds new room to database
		
			Room new_room (reverse_direction(exit));
		
			new_room.adjacent_room_add(reverse_direction(exit), current_room.room_identifier_get());
		
			Room::room_database_add (new_room);
		
		
			// adds new room as adjacent of current room, updates current room in database
		
			current_room.adjacent_room_add (exit, new_room.room_identifier_get());
		
			Room::room_database_add (current_room);
		
		
			current_room = new_room;
			
		} 
		
		
		// put character in new room
		
		character1.position_character (character1.get_position().x_axis, character1.get_position().y_axis, 
		
		current_room);
		
		
		current_room.print_adjacent_rooms();
			
	}	
	
	while (player_alive);
 	
	
	return 0;
 		
}



/*
		std::cout << "Database size:" << Room::room_database_size() << "\n\n";
		
		current_room.print_adjacent_rooms();
		
*/
