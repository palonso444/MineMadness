// <<           >>	~

/* IMPLEMENTATION (SOURCE) FILE 


Include function definitions WITHOUT default values (if any)
Include initialization of static data members (if any)  (type class::name = initial value) 
Prefix functions that belong to a class - > return type Class_name::funtion_name (also constructors and destructors)
Remove class keywords such class names, static members label, friend functions, public, private and protected labels.   
Remove data members. Keep only functions.

*/

// reference to header file. All other includes are here.
#include "crapgeon_utils.h"
  	
  	
/*	void Position::operator = (Position pos) {
		
		Position result_position;
		
		x_axis = pos.x_axis;
		y_axis = pos.y_axis;
		
		NOT NEEDED, "EQUALS TO" WORKS FINE WITH POSITIONS WITHOUT OVERLOADING
	}
	*/
	
	
	std::vector <Room> Room::room_database = {}; // initialization of static data member (vector)
	
	Room::Room (std::string doors) {	// random constructor
			 
		
		int x_axis = rand () % 25 + 5; // + 5 to ensure minimal size to fit doors
		
		int y_axis = rand () % 25 + 5; // + 5 to ensure minimal size to fit doors
		
		int other_doors = rand () % 10;
		
		
		if (other_doors < 5) other_doors = 1;
		
		else if (other_doors < 9) other_doors = 2;
		
		else other_doors = 3;
			
	
		
		char orientation_char;
		

		for (int i = 0; i < other_doors; i ++) {
			
			
			bool valid_orientation = false;	
			
			
			while (!valid_orientation) {
			
			
				int orientation = rand () % 4;	// 0 north, 1 east, 2 south, 3 west
			
			
				valid_orientation = true;
			
			
					switch (orientation) {
			
			
						case 0:
			
							orientation_char = 'N';
				
							break;
				
						case 1:
			
							orientation_char = 'E';
				
							break;
				
						case 2:
			
							orientation_char = 'S';
				
							break;
				
						case 3:
			
							orientation_char = 'W';
						 
							break;
					
			
					}
		
				
					for (char direction : doors) {
				
						if (direction == orientation_char) valid_orientation = false;
				
					}
			
				}
		
		
			doors.push_back (orientation_char);
			
		}
				
		create_room (x_axis, y_axis);
		
		create_doors (doors);
			
		
	}
	
	
	Room::Room (int x_axis, int y_axis, std::string doors) {	// constructor function, "V" for void (no doors)
			 
		create_room (x_axis, y_axis);
		
		create_doors (doors);	
		
	}
	
	
	void Room::create_room (int x_axis, int y_axis) {
		
		
		this->room.resize (y_axis);
			
		for (int i = 0; i < y_axis; i++) {	// iterates Y axis	
				
			for (int j = 0; j < x_axis; j++) { 	// iterates X axis
			
				if (i == 0 || i == y_axis - 1) room [i].push_back ('#');
					
				else if (j == 0 || j == x_axis - 1) room [i].push_back ('#'); 
					
				else room [i].push_back ('.');
					 
			}
			
		}
			
		
	}
	
	
	
	void Room::room_database_add (Room room) {
		
		
		room_database.push_back (room); // incorrect sintax, revise	
		
		
	}
	
	
	
	void Room::create_doors (std::string doors) {
			
			uppercase_doors (doors); 	// convert doors string to upper case
		
			for (char direction : doors) {
			
				if (direction == 'N') {
				
					room [0][room [0].size() / 2 - 1] = '.';
					room [0][room [0].size() / 2] = '.';
					room [0][room [0].size() / 2 + 1] = '.';
				
				} 
				else if (direction == 'S'){
				
					room [room.size () - 1][room [0].size() / 2 - 1] = '.';
					room [room.size () - 1][room [0].size() / 2] = '.';
					room [room.size () - 1][room [0].size() / 2 + 1] = '.';
					
				}
				else if (direction == 'E') {
				
					room [room.size () / 2 - 1][0] = '.';
					room [room.size () / 2][0] = '.';
					room [room.size () / 2 + 1][0] = '.';
				
				}
				else if (direction == 'W') {
				
					room [room.size () / 2 - 1][room [0].size () - 1] = '.'; 
					room [room.size () / 2][room [0].size () - 1] = '.';
					room [room.size () / 2 + 1][room [0].size () - 1] = '.'; 
				  
				   
				} 
														
			}		
															
		}	          
	
	
	void Room::uppercase_doors (std::string &doors) {
			
			
				for (char &direction : doors) {
				
					direction = toupper(direction);				
				
		}
			 
	} 
		

	void Room::print_room () {
			
		for (int i = 0; i < room.size(); i++) {
				
			for (int j = 0; j < room [i].size (); j++) {
					
				std::cout  << room [i][j] << " ";	
					
			}
						
			std::cout  << "\n";
			
		}
		  
	}
		
		
	std::vector <std::vector <char> > Room::get_vector () {
				
		return room;
			
	}
		
	
	void Character::move_character (Position start, Position end, Room &room) {
				
		room.room [end.y_axis][end.x_axis] = appearance;
		room.room [position.y_axis][position.x_axis] = '.';
		
		position = end;
				
	}
   	
	
	void Character::position_character (int x_axis, int y_axis, Room &room) {
		
		
			if (position.x_axis == -1) x_axis = room.get_vector () [0].size() -1; // coming from other room
			
			else if (position.x_axis == -2) x_axis = room.get_vector () [0].size() /2; // coming from other room 
			
			if (position.y_axis == -1) y_axis = room.get_vector ().size () -1;	// coming from other room 
			
			else if (position.y_axis == -2) y_axis = room.get_vector ().size () /2; // coming from other room 
			
			room.room [y_axis][x_axis] = appearance;
		
			position.x_axis = x_axis;
			position.y_axis = y_axis;
			
		
	}
		
		
	std::string Character::input_movement (Room &room) {
			
		
		Position end = position;
		
		bool valid_input = false;
		
		
		while(int arrow = getch()) {
 		 		
 			if (arrow == 27) arrow = getch();
 			
 			if (arrow == 91) arrow = getch();
 			
 
 			
 			if (arrow == 68) { // left
 						
 				
 				if (position.x_axis == 0) {
 					
 					
 					position.x_axis = -1; 	// depends on new room size
 					
 					position.y_axis = -2;	// depends on new room size
 					
 					return "W"; // new room with door at West
 					
 				
 				}
 				
 				
 				else {
 				
 					for (char spot : forbidden_spots) {
 				
 				
 						if (room.get_vector() [position.y_axis] [position.x_axis - 1] == spot) break;
 				
 						end.x_axis = end.x_axis - 1;
 				
 						valid_input = true;	
 						
 								
 					}
 				
 					if (valid_input) break;
 			
 				}
 			
 			}
 			
 			
 			else if (arrow == 65) { // up
 					
 				if (position.y_axis == 0) {
 					
 					
 					position.y_axis = -1;	// depends on new room size
 					
 					position.x_axis = -2;	// depends on new room size
 					
 					return "S"; // new room with door at South
 				
 				
 				}
 				
 				else {
 				
 					for (char spot : forbidden_spots) {
 				
 				
 						if (room.get_vector() [position.y_axis - 1] [position.x_axis] == spot) break;
 				
 						end.y_axis = end.y_axis - 1;
 				
 						valid_input = true;	
 						
 								
 					}
 				
 					if (valid_input) break;
 			
 				}
 			
 			}
 			
 			else if (arrow == 66) { // down
 					
 				if (position.y_axis == room.get_vector().size () - 1) {
 					
 					
 					position.y_axis = 0;
 					
 					position.x_axis = -2; // depends on new room size
 					
 					return "N"; // new room with door at North
 					
 				
 				}
 				
 				else {
 				
 					for (char spot : forbidden_spots) {
 				
 				
 						if (room.get_vector() [position.y_axis + 1] [position.x_axis] == spot) break;
 				
 						end.y_axis = end.y_axis + 1;
 				
 						valid_input = true;	
 						
 								
 					}
 				
 					if (valid_input) break;
 			
 				}
 			
 			}
 				
 			else if (arrow == 67) { // right
 					
 				if (position.x_axis == room.get_vector() [position.y_axis].size () - 1) {
 					
 					
 					position.x_axis = 0;
 					
 					position.y_axis = -2; // depends on new room size
 					
 					return "E"; // new room with door at East
 				
 				
 				}
 				else {
 				
 					for (char spot : forbidden_spots) {
 				
 				
 						if (room.get_vector() [position.y_axis] [position.x_axis + 1] == spot) break;
 				
 						end.x_axis = end.x_axis + 1;
 				
 						valid_input = true;	
 						
 								
 					}
 				
 					if (valid_input) break;
 			
 				}
 			
 			}																										
		}
																				
		move_character (position, end, room);
		
		return "V";			
	
	}
		
	
	
	void Character::forbidden_spots_add (char spot) {
		
		
		forbidden_spots.push_back (spot);
		
	}
	
	
	Position Character::get_position () {
				
		
		return position;
			
	}
		
	
	char Character::get_appearance () {
				
		
		return appearance;
			
	}
	
	
	Room Room::get_from_database (int index) {
				
		
		return room_database [index];
			
	}
  
