# Release 3 - Feb/2021 for Bright Nights

## Hotfix 1

- Added BLIND_EASY flag to "disassembly" recipes for recharging the XNU laser hydrogen fuel cells so it can be done in the dark.

- Removed NO_UNLOAD flag from XNU laser after finding out a battery loaded as magazine in a gun cannot be recharged by a vehicle recharging station or battery charger.

## JSON fixes and compatibility

- Fixed extension of compatibility for new .223 STANAG magazines to vanilla guns and included a few missed ones like the M16A4, handmade carbine and AR "pistols".

- Decreased mass of superalloy 30-round STANAG and 5.56 ETC magazines to make them somewhat lighter than the the steel STANAG one as stated in description.

- Fixed missing armor penetration bonuses to overcharged electrothermal guns (Nanogun, Anti-Drone Revolver and ER555 rifle in ADS and UDD configurations) .

- Pruned multiple "//" lines to avoid game-stopping loading errors, preserving the more relevant comments for each item as merged single lines whenever possible.

- A few other small fixes.

## Balance

- QR555 integrated suppressor no longer has a damage penalty but the base model damage modifier was altered so with integrated mods it still results in 0 (like the M16), while the carbine and SMG deal slightly more damage.

- Changed maximum range of the .223 Stockless Marksman Carbine to 18 because 11, the result from a direct copy-from range debuff of the 7.62mm version, was too little.

- Added SMC223 as a sidearm for the Bionic Soldier profession, plus a spare 20-round STANAG magazine. Stored in a XL holster of course. Did not change points cost as the bionics are a much bigger deal.

- Replaced the Police Sniper sidearm with a SMC308 plus two speedloaders for it and more loose 7.62x51mm rounds. A major tradeoff of magazine capacity for firepower.

- Replaced the Bionic Sniper sidearm with the SMC300, plus two ankle ammo pouches with M2010 ESR magazines and the bionic sniper M2010 ESR had the magazines meant for it replaced with the 10-round SMC300 ones so the starting guns remain useful a bit longer.

- Replaced Glock 18C from the Bionic Police Officer with a OCG-Leadworks 923, plus 30-round magazines instead of 17-round ones to bring back the not-Robocop pistol now bigger and therefore better.

- Replaced 12C Storm Bolter and 923 machine pistol from the Leadworks Executive with a Combo X912 and added an extra 30-round magazine and leg ammo pouch.

- Changed the used skill by vanilla AR-15 based "pistols" from rifles to handguns like in the AK-47 based Draco (this change may become redundant in future BN and/or DDA releases)

- Added rifle caliber "pistols" to one more spawn list where they are appropriate. Still should be very rare regardless of this.

- Changed battery tool mods so they can be switched between mods for tools or loading port mods for any gun that uses batteries as ammo, except for the UPS conversion mod. Only the new XNU laser supports such battery mods as gunmods.

## New Content

- QSMG-9, a bullpup, integrally suppressed 9mm submachinegun that is nothing more than a rechambered QR555 with a new receiver using MR9 DMSMG casket magazines.

- Combo 912, the really big modern stepbrother of the LeMat revolver, a combination of a 9mm pistol with 12 gauge underbarrel double barrel shotgun that can shoot both barrels at once. Can be "illegally" converted to a 9mm machine pistol with shotgun.

- American Eagle and American Bear .357, very flexible gas-operated pistol and rifle that can use .357 magnum, .357 SIG or .38 special but are big, bulky, heavy and limited in magazine capacity.

- XNU near-ultraviolet laser, a very powerful energy weapon with its own rechargeable hydrogen fuel cell that uses replaceable solid hydrogen canisters. The cell recharging process is currently a bit hacky and uniquely features clean water as byproduct.

- X12P plasma shotgun, which instead of having explosions features a "bounce" effect(chain reaction of spontaneous combustions), making it a very powerful anti-horde gun if incinerating loot is not a problem. However, it guzzles 200 UPS charges per shot.

- Doomed Marine / Alice McGee asymmetric profession. The latter has more melee weapons while both have the Killer Drive and Psychosis traits and carry more than enough weaponry to protect or avenge the pet rabbit even when knee-deep in the dead.