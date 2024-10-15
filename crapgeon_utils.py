
"""
Program agnostic utilities.
"""

def tuple_remove(some_tuple, item) -> tuple:
    # DEPRECATE
    tuple_to_list = list(some_tuple)
    tuple_to_list.remove(item)
    return tuple(tuple_to_list)

def check_if_multiple(number: int, multiple_of: int):
    # MOVE TO MINEMADNESSGAME METHOD check if players turn
    return number % multiple_of == 0
