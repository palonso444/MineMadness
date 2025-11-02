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


	
	std::vector <Room> Room::room_database = {}; 
	
	
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
		
		
		room_identifier = Room::room_database_size();
		
		this->room.resize (y_axis);
			
		for (int i = 0; i < y_axis; i++) {	// iterates Y axis	
				
			for (int j = 0; j < x_axis; j++) { 	// iterates X axis
			
				if (i == 0 || i == y_axis - 1) room [i].push_back ('#');
					
				else if (j == 0 || j == x_axis - 1) room [i].push_back ('#'); 
					
				else room [i].push_back ('.');
					 
			}
			
		}
			
			
	}
	
	
	void Room::adjacent_room_add (std::string direction, int identifier) {
		
		
		adjacent_rooms.insert(std::pair <std::string, int> (direction, identifier));
		
		
	}
	
	
	int Room::adjacent_room_get (std::string direction) {
		
		
		return adjacent_rooms [direction];
		
		
	}
	
	int Room::room_identifier_get () {
		
		
		return room_identifier;
		
		
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
				else if (direction == 'W') {
				
					room [room.size () / 2 - 1][0] = '.';
					room [room.size () / 2][0] = '.';
					room [room.size () / 2 + 1][0] = '.';
				
				}
				else if (direction == 'E') {
				
					room [room.size () / 2 - 1][room [0].size () - 1] = '.'; 
					room [room.size () / 2][room [0].size () - 1] = '.';
					room [room.size () / 2 + 1][room [0].size () - 1] = '.'; 
				  
				   
				} 
														
			}		
															
		}	          
	
	
	void Room::uppercase_doors (std::string doors) {	//in case of error pass doors by reference (&)
			
			
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
		
		
	std::string reverse_direction (std::string direction) {
			
			
			if (direction == "N") direction = "S";
			
			else if (direction == "S") direction = "N";
			
			else if (direction == "E") direction = "W";
			
			else if (direction == "W") direction = "E";
			
			return direction;
			
		}
	
	
	bool Room::door_was_crossed (std::string direction) {
		
		
		
		//std::map <char, int>::iterator it; 
		
		//it = room_borders.find (direction);
		
		if (adjacent_rooms.find (direction) == adjacent_rooms.end ()) return false;
		
		return true;
		
		
		
	}
	
	
	Room Room::room_database_get (int identifier) {
		
		
		for (Room room : room_database) {
			
			if (room.room_identifier == identifier) return room;
			
		}
			
		std::cout << "Error: room not found";
		
		return room_database [0];
	
	}
	
	
	
	std::vector <std::vector <char> > Room::get_vector () {
				
		return room;
			
	}
	
	
	void Room::room_database_add (Room room) {
		
		for (Room &in_database : room_database) {
			
			if (in_database.room_identifier == room.room_identifier) {
				
				in_database.adjacent_rooms = room.adjacent_rooms;	//if found, update
				
				return;
			
			}
			
		}
		
		room_database.push_back (room);	//if not found, add
		
	}
	
	
	int Room::room_database_size() {
		
		
		return room_database.size();
		
		
	}
	
	
	void Room::print_adjacent_rooms () {
		
	
		for(std::map <std::string, int>::const_iterator it = adjacent_rooms.begin();
   		
 it != adjacent_rooms.end(); ++it) {
    
    
    		std::cout << it->first << " " << it->second << "\n";


		}

	}
	
