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
		
		NOT NEEDED, "EQUALS TO" WORKS FINE WITH CUSTOM TYPES WITHOUT OVERLOADING
	}
	*/
			
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
 					
 					return "W"; 
 					
 				
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
 					
 					return "N";
 				
 				
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
 					
 					return "S";
 					
 				
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
 					
 					return "E";
 				
 				
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
  
