/* HEADER FILE 

include only:

Function declarations and default values (if any). End definitions with semicolon (;)
Struct structures
Class structures
Class data members and default values (if any)
Do not mention in compilation step (mention only .cpp files)

*/

// preprocessor directives not to include this file more than once when compiling
#ifndef CRAPGEON_UTILS 
#define CRAPGEON_UTILS
 
#include <iostream>
#include <vector>
#include <string>
#include <conio.h>
#include <ctime>
#include <map>


struct Position {
	
	
	int x_axis;
	int y_axis;
	
	//void operator = (Position pos);	not needed, "equals to" works fine with positions without overloading
		
};


class Room;	// needed to be declared here due to friend function move_character in Character class


class Character {
	
	
	std::vector <char> forbidden_spots = {'#'};  //walls are not allowed for anybody
	
	char appearance = '%';
	
	int speed;
	
	Position position;
	
	
	
	public:
	
		
		std::string input_movement (Room &room);	// input movement of character using arrow keys.
		
									// returns direction of new room door if character leaves room. 
							
									// Else calls move_character
		
		
		void move_character (Position start, Position end, Room &room);	// move character after input
		
		void position_character (int x_axis, int y_axis, Room &room);	//places character in new room
		
		
		void forbidden_spots_add (char spot);
		
		Position get_position ();
		
		char get_appearance ();		

};



class Room {
	
	
	static std::vector <Room> room_database;
	
	
	std::map <std::string, int> adjacent_rooms; // record of adjacent rooms (key direction, value room_identifier) 
	
	std::vector <std::vector <char> > room;
	
	int room_identifier; 	//equals to its index in vector room_database
	
	
	void uppercase_doors (std::string doors);
		          
	void create_doors (std::string doors);	// called by constructors, sets up doors
	
	void create_room (int x_axis, int y_axis);	// called by constructors, sets up room area
			
	
	
	public:
	
		
		
		Room (std::string doors = "V");	//randomized constructor, "V" for void (no doors)
		
		Room (int x_axis, int y_axis, std::string doors = "V");	// constructor, "V" for void (no doors)
		
		
		static int room_database_size();	// returns number of rooms
		
		static Room room_database_get (int identifier); //gets adjacent room from room_database
		
		static void room_database_add (Room room);
		
		
		int room_identifier_get ();	//returns the identification number of the room
		
		void adjacent_room_add (std::string direction, int identifier);	//adds room to adjacent_rooms database
		
		int adjacent_room_get (std::string direction);	//returns identifier of adjacent room
		
		void print_adjacent_rooms (); //prints direction and identifier of adjacents rooms
		
		
		bool door_was_crossed (std::string direction);	// returns true if player already crossed that door
		 
		 
		void print_room ();
		
				
		std::vector <std::vector <char> > get_vector ();  //returns vector room
		
		
		friend void Character::position_character (int x_axis, int y_axis, Room &room);
		
		friend void Character::move_character (Position start, Position end, Room &room);
   	
};


std::string reverse_direction (std::string direction);	// reverses directions (Ex. N becomes S). PUT IN SEPARATE FILE




// end of preprocessor directive
#endif
