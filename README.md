The purpose of this branch is to get rid of all unnecessary switches or minemadness_game: 
- gems
- character_id (see issue 283)
- and all other in the method force_update method) and of the method force_update itself.
- Inventory object. Property must be triggered when object is added to the dictionary of the character, not manually via Stringproperty
- Also, it may have some bugs, see at the end of the file:


![mine_madness](https://github.com/user-attachments/assets/f7495fcb-5e02-406b-9c3b-5f7fd324362c)


Welcome to the underground madness!
-----------------------------------

FEATURING:

Random level generation - each experience is unique!

Monsters with variable AI - from wanderers to merciless hunters.

2 game modes - Hardcore, and even more Hardcore!

This game has been developed in Python using the Kivy framework.

It has been thoroughly tested, but some bugs may lurk in the shadows. If you encounter any issues or have any suggestions, please feel free to leave your feedback in the comments in the itch.io page.

NOTE: The flickering of the torches may cause performance issues on some devices. If this occurs, the feature can be disabled in the Options Menu.

WARNING: Although this game is available for Windows and Android, only the Android version is properly balanced and tested. The Windows version is only for demonstration purposes.


Itch.io page to download the game
---------------------------------
https://palonso444.itch.io/minemadness

![mobile1](https://github.com/user-attachments/assets/f9fec359-d6b4-49f8-a69f-1e7eed695b77)
![mobile3](https://github.com/user-attachments/assets/3b3562ac-5640-44a9-ab98-43186c618850)


Developer notes
---------------

This is a experimental branch. It uses events instead of manually triggering switches. It has several bugs:

1. Some monsters move simultaneously sometimes. usually when a character exits. not clear why

2. When killing last monster of dungeon, program breaks
