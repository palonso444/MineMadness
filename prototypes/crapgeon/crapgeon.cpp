// <<           >>

struct Position {
	
	
	int x_axis;
	int y_axis;
	
	// operator overload to compare positions ==!!
		
};


class Room {
  	
	
	std::vector <std::vector <char> > room;
	
	
	void uppercase_doors (std::string &doors) {
			
			
				for (char &direction : doors) {
				
				direction = toupper(direction);				
				
		}
			 
	} 
	
		          
	void create_doors (std::string doors) {
			
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
	
	
	public:
	
		
		Room (int x_axis, int y_axis, std::string doors = "V") {	// constructor function, "V" for void (no doors)
			 
			room.resize (y_axis);
			
			for (int i = 0; i < y_axis; i++) {	// iterates Y axis	
				
				for (int j = 0; j < x_axis; j++) { 	// iterates X axis
			
					if (i == 0 || i == y_axis - 1) room [i].push_back ('#');
					
					else if (j == 0 || j == x_axis - 1) room [i].push_back ('#'); 
					
					else room [i].push_back ('.');
					 
				}
			

			}
		
		create_doors (doors);	
		
		}
		

		void print_room () {
			
			for (int i = 0; i < room.size(); i++) {
				
				for (int j = 0; j < room [i].size (); j++) {
					
					std::cout  << room [i][j] << " ";	
					
				}
						
				std::cout  << "\n";
			
			}
		  
		}
		
		
		void allocate_character (int x_axis, int y_axis, char appearance) {
				
			room [y_axis][x_axis] = appearance;
					
		}
		
		
		std::vector <std::vector <char> > get_vector () {
				
			return room;
			
		}
		
		void move_character (Position start, Position end, char appearance) {
				
			clrscr();
			
			room [end.y_axis][end.x_axis] = appearance;
			room [start.y_axis][start.x_axis] = '.';
					
		}
   	
};



class Character {
	
	
	char appearance = '%';
	
	int speed = 1;
	
	Position position;
	
	std::vector <std::vector <char> > parent;
	
	
	
	public:
	
	
		void position_character (int x_axis, int y_axis, Room &room) {
		
		
			if (room.get_vector () .size () <= y_axis || room.get_vector () [y_axis].size () <= x_axis || x_axis < 0 || y_axis < 0) std::cout << "\n Failed to position character at x = " << x_axis << " y = " << y_axis << ".Position falls outside room.\n\n";  
		
			else if (room.get_vector () [y_axis] [x_axis] != '.') std::cout  << "\n Failed to position character at x = " << x_axis << " y = " << y_axis << ". Position already occupied.\n\n"; 
		
			else {
		
				room.allocate_character (x_axis, y_axis, appearance);
		
				position.x_axis = x_axis;
				position.y_axis = y_axis;
				
				parent = room.get_vector();
					
		
			}
		
		}
		
		
		Position input_movement() {
			
			 
			 while(int arrow = getch()) {
 		 		
 				if (arrow == 27) arrow = getch();
 			
 				if (arrow == 91) arrow = getch();
 			
 				if (arrow == 68) {
 					
 					if (parent [position.y_axis] [position.x_axis - speed] == '.')  {
 						
 						position.x_axis = position.x_axis - speed;
 						return position;
 						
 					}
 					
 				} //left
 			
 				else if (arrow == 65) {
 					
 					if (parent [position.y_axis - speed] [position.x_axis] == '.') {
 						
 						 position.y_axis = position.y_axis - speed;
 						 return position;
 						  
 						    }
 				
 				} //up
 			
 				else if (arrow == 66) {
 					
 					if (parent [position.y_axis + speed] [position.x_axis] == '.')  {
 						
 						position.y_axis = position.y_axis + speed;
 						return position;
 						
 						
 					}	 
 					  
 				} //down
 				
 				else if (arrow == 67) {
 					
 					if (parent [position.y_axis] [position.x_axis + speed] == '.') {
 						
 						
 						position.x_axis = position.x_axis + speed;
 						return position;
 						
 					}
 							
 				} // right												
																							}			
	
		}
		
		Position get_position () {
			
			
			return position;
			
		}
		
		char get_appearance () {
			
			
			return appearance;
			
		}

};
 


int main () {
 	
 	Room room1 (30,20, "N");
 	
 	Character character1;
 	
 	character1.position_character (18,18,room1);
 	
 	room1.print_room ();
 	
 	
 	for (int i = 0; i < 30; i++) {
 	
 	Position start = character1.get_position (); // include this inside move_character function
 	
 	Position end = character1.input_movement(); // include this inside move_character function. Overload to distinguish monster or hero. Each class will inherit one version of input_movement function.
 	
 	room1.move_character (start, end, character1.get_appearance()); // here is better to pass character name, appearance may be get from inside move_character function
 	
 	room1.print_room ();
 	
 	}          
 	
 	
 	return 0;
 	
 	
 	}




