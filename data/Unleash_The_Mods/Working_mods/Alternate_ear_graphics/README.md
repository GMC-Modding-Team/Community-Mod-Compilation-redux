# Alternate ear graphics
A small mod I threw together which replaces certian mutation graphics with ones i'd redesigned. 
FULL DISCLAIMER, I designed these alternate graphics for a particular character of mine! I only made this because a few people seemed interested. Use this with the understanding that these graphics arent intended to work with all the different appearances your character can take, if the colour is the problem ive added a selection of pallets  (see V1.1 texture replacement below) but otherwise just understand results may vary.


## Dependencies
Requires [UndeadPeopleTileset](https://github.com/SomeDeadGuy/UndeadPeopleTileset). 
The go to tileset for CDDA by this point and for good reason, its great!

## Installation
So i neglected to consider people who arent used to installing mods, so i thought id take the time to do a brief walkthrough of the process.
> 1 - Download the directory - Click clone directory, then click download zip. You can download this anywhere you want, the file will be called 'CDDA-Alternate-ear-graphics-master' and will be in your 'downloads' folder.

> 2 - Unzip the directory - Unzip the directory, if you dont know what this means look it up. Its fairly common thing when downloading most mods for anything.

> 3 - Copy the mod file - Open the unziped 'CDDA-Alternate-ear-graphics-master' file and copy the file called 'Alternate ear graphics'

> 4 - Locate your mod folder for CDDA - Find where you installed the game, if you used the launcher it will be installed in the launcher file, then follow the path 

> installation location/CDDA Game Launcher/cdda/data/mods 

> (if you didnt use the launcher follow the same path excuding the game laucher file).

> 5 - Paste the mod file into the mods folder - Pretty simple, this mod will now be in the addon list for when you create a new world!

### Enabling the mod mid-game
Whats that? you dont want to have to make a new world? You want to keep doing cool things in your current one? Not to worry! Just follow these additional steps!
> 1 - Locate your save file for CDDA - Specifically CDDA saves games by world so your finding the world file. Follow the path 

> Installation location/CDDA Game Launcher/cdda/save

> Then open the file with the name of your current world.

> 2 - Find and open the mods.json file - Opening it in notepad will work, you should see a short list of names in "". 

> 3 - Edit in the mod name - Just add another line near the top of the list and write '"alt_ear_gfx",' ATTENTION! that comma is important, every name except the last in the list should have one outside the "" or the game cant read it.

> 4 - Save the changes - Congratulations! If you did it right the mod should now be enabled for your current world.


## Usage Guide
This mod can be enabled mid-game, all it does is replace a few textures and add a few extra recipes. 

The ears arent covered properly by hats so make some of the cosmetic ears to layer ontop if your character has headwear. Ideally i'd make these specific mutations render over clothes but apparently that would take a load of C++ sorcery and i aint no harry potter.

### V1.1 Texture replacement
With v1.1 you now have a Texture folder with a selection of the mutation graphics in a selection of colour pallets, which means you can now choose a colour which better matches your characters hair colour! 

To change the texture colours, follow these steps:
> 1 - Open the /Alternate_ear_graphics/Textures folder, inside you will find a Hair_hue_index.png and a library of folders sorted by colour and variant. If you're unsure which variant you are looking for, consult the Index. 

> 2 - To replace the in game textures, first open the folder for the colour you want and then copy both .png files, return to /Alternate_ear_graphics and  replace the existing .png files here.

> 3 - If open, restart the game. The changes should now have been applied!

The graphics can be swapped at any time, and the changes will register once you restart the game. If the colour you chose didnt suit your characters hair colour, refer again to the Hair_hue_index.png to see if there isnt a colour category that better suits it.


## Versions
v1.0 - Adds New mutation texures for Canine/ Lupine and Feline ears, as well as for the Fluffy tail mutation. Also adds recipies for ear mutation mimic hats for layering ontop of other headwear.

v1.1 - Adds Repository of mutation textures with different colour pallets designed to match most hair colours.
> v1.1.1 - Corrects all tail sprites Y offset to be one pixel lower.

> V1.1.2 - Added installation guides to the README.md .


## Issues
At the time of this writing, all the features in this mod are tested and work as intended. Lets hope that lasts!
