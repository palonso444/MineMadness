
"""
Program agnostic utilities.
"""

def match_attribute_to_item(attributes: list[str]) -> list[str]:
    """
    Converts a list of attributes to a list of items that modifies them
    """

    items = list()
    for attribute in attributes:
        match attribute:
            case "moves":
                items.append("coffee")
            case "thoughness":
                items.append("tobacco")
            case "strength":
                items.append("whisky")
    return items


def tuple_remove(some_tuple, item) -> tuple:

    tuple_to_list = list(some_tuple)
    tuple_to_list.remove(item)
    return tuple(tuple_to_list)


def check_if_multiple(number: int, multiple_of: int):

    if number % multiple_of == 0:
        return True
    return False

