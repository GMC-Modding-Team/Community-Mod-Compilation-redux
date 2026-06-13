# Key bindings

Use the `home` key to get to the top.

Currently a copy+paste of http://cddawiki.chezzo.com/cdda_wiki/index.php?title=Controls

with punctuation updates and removed descriptions, until update.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Controls](#controls)
  - [Default key bindings](#default-key-bindings)
    - [Movement](#movement)
    - [Shift view](#shift-view)
    - [Environment interaction](#environment-interaction)
    - [Inventory and quasi-inventory interaction](#inventory-and-quasi-inventory-interaction)
    - [Item action menu](#item-action-menu)
    - [Long term and special actions](#long-term-and-special-actions)
    - [Info screens](#info-screens)
    - [Debug functions](#debug-functions)
  - [Advanced Controls](#advanced-controls)
    - [Advanced Inventory](#advanced-inventory)
    - [Advanced Inventory Directional Controls](#advanced-inventory-directional-controls)
    - [Auto Pickup](#auto-pickup)
  - [Unlisted key bindings](#unlisted-key-bindings)
  - [Further controls and procedures](#further-controls-and-procedures)
    - [Remove wielded item](#remove-wielded-item)
    - [Dropping Items](#dropping-items)
      - [Single items](#single-items)
      - [Dropping Partial Stacks](#dropping-partial-stacks)
    - [Picking up Items](#picking-up-items)
    - [Controlling Skill Gain](#controlling-skill-gain)
    - [Talking to NPC's or Yelling](#talking-to-npcs-or-yelling)
  - [Debug keys](#debug-keys)
    - [Edit player/NPCs](#edit-playernpcs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
# Controls

Controls can be customized in Main Menu `(ESC)`, Keybindings submenu (1). The current key bindings are stored in the `config/keybindings.json` file. To revert back to defaults just delete it.

## Default key bindings

All the listed key binds are case sensitive (so an a is different from an A, etc).

### Movement

|       NW       |       N        |       NE        |
| :------------: | :------------: | :-------------: |
|     7 or y     |  8 or k or UP  |     9 or u      |
|       W        |     PAUSE      |        E        |
| 4 or h or LEFT |     5 or .     | 6 or l or RIGHT |
|       SW       |       S        |       SE        |
|     1 or b     | 2 or j or DOWN |     3 or n      |

`>` - Descend stairs

`<` - Ascend stairs

`"` - Toggle walk/run/crouch

### Shift view

You can permanently shift the centering of the viewport by using these keys:

|  SHIFT NW   |   SHIFT N   |  SHIFT NE   |
| :---------: | :---------: | :---------: |
| *<Unbound>* |      K      | *<Unbound>* |
|   SHIFT W   | CENTER VIEW |   SHIFT E   |
|      H      |      :      |      L      |
|  SHIFT SW   |   SHIFT S   |  SHIFT SE   |
| *<Unbound>* |      J      | *<Unbound>* |

### Environment interaction

| Key     | Command                                                      |
| ------- | ------------------------------------------------------------ |
| o       | Open door or window.                                         |
| c       | Close door or window.                                        |
| s       | Smash nearby object / Vehicle handbrake.                     |
| e       | Examine or interact with nearby world object.                |
| /       | Advanced inventory management.                               |
| , or g  | Pick item(s) up.                                             |
| G       | Grab a nearby vehicle/furniture / Release vehicle/furniture. |
| B       | Butcher a corpse.                                            |
| C       | Chat with an NPC, or Yell to make a bit of noise.            |
| ; or x  | Look around.                                                 |
| X       | Peek around corners, down stairs, and allows the blind throwing of grenades. |
| Shift+V | List all items/creatures around the player.                  |
| \       | Drag all items you are currently standing on, press again to stop dragging. |

###  Inventory and quasi-inventory interaction

| Key       | Command                                 |
| :---- | --------------------------------------- |
| i     | Open your inventory.                    |
| I     | Compare two items.                      |
| =     | Swap inventory letters.                 |
| a     | Apply or use an item.                   |
| A     | Apply or use currently wielded item.    |
| W     | Wear item.                              |
| T     | Take off worn item.                     |
| E     | Eat/Drink/Consume item.                 |
| R     | Read a book or a magazine.              |
| w     | Wield item.                             |
| _     | Select unarmed style.                   |
| r     | Reload wielded item.                    |
| U     | Unload or empty wielded or nearby item. |
| t     | Throw item.                             |
| f     | Fire wielded item.                      |
|       | Burst.                                  |
| F     | Toggle attack mode of wielded item.     |
| d     | Drop item.                              |
| D     | Drop item to adjacent tile.             |
| p     | View/Activate bionics.                  |
| +     | Re-layer armour/clothing.               |
| {     | View/Activate mutations.                |

### Item action menu

| Key  | Command                |
| ---- | ---------------------- |
| %    | Access list of actions |



### Long term and special actions

| Key  | Command                        |
| ---- | ------------------------------ |
| \    | Wait for several minutes.      |
| &    | Craft items.                   |
| -    | Re-craft last recipe.          |
|      | Craft for as long as possible. |
| *    | Construct terrain.             |
| (    | Disassemble items.             |
| $    | Sleep.                         |
| ^    | Control vehicle.               |
| !    | Toggle Safemode.               |
| "    | Toggle Auto-Safemode.          |
| '    | Ignore nearby enemy.           |
| S    | Save and quit.                 |
|      | Quicksave.                     |
| Q    | Commit suicide.                |

### Info screens

| Keys | Command           |
| ---- | ----------------- |
| @    | View player info. |
| m    | View map.         |
| M    | View missions.    |
| #    | View factions.    |
| )    | View kill count.  |
| v    | View morale.      |
| P    | View message log. |
| ?    | View help.        |

### Debug functions

| Keys | Command                |
| :--: | ---------------------- |
|      | Debug menu.            |
|      | View scentmap.         |
|  ~   | Toggle debug messages. |

## Advanced Controls

All controls in the game as of June 7, 2019. Not up to date.

### Advanced Inventory

| Keys              | Command                            |
| ---- | ---------------------------------- |
| /                 | Enter advanced inventory.          |
| s/S               | Change sorting mode.               |
| e/E               | Examine item.                      |
| RETURN            | Move a single item.                |
| ,                 | Move all items.                    |
| m                 | Move an amount of an item.         |
| M                 | Move item stack.                   |
| >                 | Page down.                         |
| <                 | Page up.                           |
| DOWN,j,JOY_DOWN   | Pan down.                          |
| UP,k,JOY_UP       | Pan up.                            |
| <unbound>         | Restore default layout.            |
| <unbound>         | Save default layout.               |
| w/W               | Select items currently worn.       |
| c/C               | Select items in container.         |
| d/D               | Select items in dragged container. |
| 0/i/I             | Select items in inventory.         |
| LEFT,h,JOY_LEFT   | Select left inventory.             |
| RIGHT,l,JOY_RIGHT | Select right inventory.            |
| a/A               | Select all items.                  |
| p                 | Toggle auto-pickup for item.       |
| t                 | Toggle category selection mode.    |
| *                 | Toggle item as favorite.           |
| TAB               | Toggle tab.                        |
| v/V               | Toggle vehicle.                    |

### Advanced Inventory Directional Controls

| Select items @ NW |   Select items @ N    | Select items @ NE |
| :---------------: | :-------------------: | :---------------: |
|         7         |           8           |         9         |
| Select items @ W  | Select items @ Center | Select items @ E  |
|         4         |           5           |         6         |
| Select items @ SW |   Select items @ S    | Select items @ SE |
|         1         |           2           |         3         |

| Keys | Command                      |
| ---- | ---------------------------- |
| a/A  | Select items at all 9 fields.|



### Auto Pickup

| Keys | Command                        |
| ---- | ------------------------------ |
| a/A  | Add rule.                      |
| c/C  | Copy rule.                     |
| d/D  | Disable rule.                  |
| s/S  | Enable auto pickup option.     |
| e/E  | Enable rule.                   |
| -    | Move rule down.                |
| m/M  | Move rule global <-> character.|
| +    | Move rule up.                  |
| r/R  | Remove rule.                   |
| t/T  | Test rule.                     |

## Unlisted key bindings

| Keys      | Command                         |
| --------- | ------------------------------- |
| ESC/SPACE | Exit dialog or screen / Cancel. |
| ,         | Select/Deselect all items.      |

## Further controls and procedures

Here you'll find some actions and procedures that aren't obvious or simply not explained anywhere else.

### Remove wielded item

To remove the item you're currently wielding so your hands are empty (fists) go through the following key sequence:

1. Press `w`
2. Choose currently wielded item

If you previously selected a [martial arts](http://cddawiki.chezzo.com/cdda_wiki/index.php?title=Martial_arts) style through `_` it'll revert to that MA style instead.

In any case, the currently wielded item will be automatically placed in your inventory, or you'll be asked if you want to drop it if there's no space left.

### Dropping Items

#### Single items

Dropping an item from the `i`nventory screen will always drop a single item.

#### Dropping Partial Stacks

1. Press `d` or `D` to drop the items and display the inventory screen
2. Type the number of items you want to drop
3. Press again the key of the inventory item you want to divide (in some cases, this will cause the item letter to be displayed as #)
4. Press `RETURN`

### Picking up Items

Pressing `,` twice selects all items. Currently this functionality cannot be reassigned to another key.

### Controlling Skill Gain

1. Open the `@` Character Status screen
2. Use `TAB` to navigate to the SKILLS section.
3. Use the `arrow keys` to navigate the SKILLS list.
4. Press `SPACE` when having selected the skill you want to freeze skill-gain.
5. Press that key again to reactivate it.

### Talking to [NPC's](http://cddawiki.chezzo.com/cdda_wiki/index.php?title=NPC) or Yelling

Press the `C` key. Select the option from the menu.

## Debug keys

Note: Use of these keys is essentially [**CHEATING**](http://cddawiki.chezzo.com/cdda_wiki/index.php?title=Cheating), unless you are in a situation caused by bugs (e.g. spawning in a windowless doorless room) or testing game features.

`~` — Toggle debug messages.

*Unbound* — *Scent map.* Asks you what scent sensitivity you would like to view your surrounding with (0-9, 1 greatest smeller, 9 dullest nose, **0 divides by 0, causing a crash**). Shows the trace that forms around you as you linger in a building or move through town.

There is also the debug menu.

To enable this menu, you will need to edit the Controls. Go to the main menu by pressing Esc followed by the keybindings list by pressing 1. Close to the bottom of the list will be the Debug Menu which should be in red and unbound. Press `+` followed by the appropriate letter to assign a key of your choice. Note: many keys are already bound to other features, using the `` ` key is a good option as it's unbound by defaultVerify (Not by keybindings.json...) and is in the same place as the Debug messages and Console Commands present in many PC games.

| Keys | Command                       |
| ---- | ----------------------------- |
|      | *Debug menu.*                 |
| 1    | Wish for an item.             |
| 2    | Teleport - Short Range.       |
| 3    | Teleport - Long Range.        |
| 4    | Reveal map.                   |
| 5    | Spawn NPC.                    |
| 6    | Spawn Monster.                |
| 7    | Check game state...           |
| 8    | Kill NPCs.                    |
| 9    | Mutate.                       |
| 0    | Spawn a vehicle.              |
| a    | Change all skills.            |
| b    | Learn all melee styles.       |
| c    | Unlock all recipes.           |
| d    | Edit player/NPC.              |
| e    | Spawn Artifact.               |
| f    | Spawn Clairvoyance Artifact.  |
| g    | Map Editor.                   |
| h    | Change weather.               |
| i    | Kill all monsters.            |
| j    | Display hordes.               |
| k    | Test Item Group.              |
| l    | Damage self.                  |
| m    | Show Sound Clustering.        |
| o    | Display weather.              |
| p    | Display overmap scents.       |
| q    | Change time.                  |
| r    | Set automove route.           |
| m    | Show mutation category levels.|
| t    | Overmap editor.               |
| u    | Cancel.                       |



### Edit player/NPCs

Looking at an NPC with this debug feature shows the name, class, destination, internal values (Trust, Fear, Anger, Owed, Aggression, Bravery, Collector, Altruism, and the needs of the NPC.

| Keys | Command                                         |
| ---- | ----------------------------------------------- |
| s    | Edit skills.                                    |
| t    | Edit Stats.                                     |
| i    | Grant items.                                    |
| d    | Delete all items.                               |
| w    | Wear/Wield an item from NPC/Player's inventory. |
| h    | Set hit points.                                 |
| p    | Cause pain.                                     |
| a    | Set health.                                     |
| n    | Set needs.                                      |
| u    | Mutate.                                         |
| @    | Status Window.                                  |
| e    | teleport.                                       |
| m    | Add mission.                                    |
| c    | Randomize with class.                           |
| q    | quit.                                           |
