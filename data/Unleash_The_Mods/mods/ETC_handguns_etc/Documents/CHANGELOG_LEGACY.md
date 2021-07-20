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



# Release 2 - Jan/2021 for Bright Nights (not tested in mainline 0.E but should work too)

## JSON fixes and compatibility

- Adjusted syntax and content of all .json files for compatibility.

- Fixed Corporate Spymaster profession to properly carry a .22 ETC stealth pistol.

- Fixed Vault Newcomer challenge starting location which should never mismatch now, just one level further undeground because keeping it in the same Z-level as before won't work. Guaranteed !FUN! increase.

- Set up new migration settings for Leadworks guns removed from vanilla to the "reimagined" versions for the 1 in one billion odds of someone trying this mod and having a save that will benefit from this.

## Balance

- Removed all non-exclusive gun mods, replaced with vanilla ones. Gyroscopic stabilizers in rifle caliber "pistols" were replaced with folding wire stocks.

- Adjusted rate of fire of automatic weapons to match changes in the vanilla weapons autofire specs and remain balanced in relation to them.

- Added folding wire stocks to some guns which recoil and rate of fire really makes having no stock at all in them madness.

- Adjusted firearms dimensions to a balanced match between realism and fun, also to fit properly with the new maximum volume restrictions of holsters according to their intended purposes(backup pistol, fast draw main pistol, big main pistol, etc).

- Reduced capacity of the O9 electromagnum and doublemag to only 4 rounds, matching the bigger 5.56 ADR and 7.62 AMR and allowing the same speedloader to also be used by a new 9mm derringer. Reduced their volume accordingly to also fit in fast draw holsters.

- Migrated damage that should be from the rounds to the rounds JSON instead of having the total damage value split between rounds and guns for noise reduction and defined specific loudness values for all pistol caliber ETC bullets.

- Rebalanced several .22 ETC and 9mm ETC rounds specs with a more drastic gradient in stopping power vs. armor penetration among different ammo types. IE: .22 ETC microflechette - 9 dmg and 60 AP vs. .22 ETC TB - 27 dmg and 0 AP.

- Buffed base stopping power of .22 ETC by 20%  to match the rebalance of .22 in Bright Nights. Damage value for default APM rounds increased to 18 (2 points above .22 LR).

- Changed .308 SMC from being compatible with only M14 magazines to using its own non-detachable tubular magazine.

- Changed starting weapons for the corporate spymaster profession. EMP Projector was replaced with a YM14 PDW loaded with 10mm Auto plus 2 spare magazines while the 12C Storm Bolter shotgun was replaced with a modded and scoped V29 laser pistol.

- Gave the corporate spymaster a new and completely exclusive, never spawned anywhere starting gun: a crazy slam fire only shotgun prototype.

- Some small adjustments to spawn distribution and the new stuff added to spawns of course.

## New Content

- Added tube loaders for the new guns with magazine tubes, speedloaders for the new revolvers and alike.

- One magazine fed triple barrel .410 shotgun, the OCG410 Triarii, to put the nuts in gun nuts.

- One automatic, SMG-like .410 shotgun, the OCG410A SBMP, because there is no spray and pray like loading a magazine in a shotgun similarly to how one is loaded in a MAC-10 then trying to control the muzzle climb once buckshot starts flying.

- One theoretically possible if not necessarily practical compact .410 shotgun vaguely resembling a Micro-Uzi with an integral suppressor for "silent" breaching or madmen who want a "silenced" shotgun instead of a SMG; The OCG-410S Sicarius.

- OCG 12D Slam Dunk as an exclusive starting gun for the Corporate Spymaster profession, a prototype that was not yet put into production when the cataclysm happened, perhaps for a good reason, but quite powerful, with a higher sustained rate of fire than most shotguns.

- YM14 Carbine PDW, a pistol caliber carbine designed to emulate the stopping power and range of the M1 carbine with 10mm auto, also compatible with .40 S&W. Plus a 6-round backup pistol and a variant of the chaingun rechambered for these calibers too.

- "Restored" the Enforcer autorevolver as the OCG-Leadworks 460 with some changes: ammo capacity reduced from 6 to 5, uses vanilla holographic sight and a detachable laser sight and is compatible with more gun mods if becoming too big for a normal holster isn't a problem.

- Added .45 colt and .410 shot variant of the Leadworks Enforcer as OCG-Leadworks 45 Sixpack. Sixpack of Colt45 not included. Don't load it with blackpowder rounds.

- Reimagined the L12 Defender as the OCG-Leadworks 12C Storm Bolter. Sort of like a double barrel Serbu Firearms Super-Shorty Mini-Shotgun. While a bootleg Winchester 1887 has a larger magazine, this one has among other advantages a preposterous origin story, for it was crowdfunded by big fans of the Cataclysm universe equivalent to Warhammer 40k."

- Reimagined the 9mm Leadworks L9 Lookout revolver as the OCG-Leadworks Quad9 holdout derringer. Small enough for any holster, it fires all its four barrels simultaneously and is compatible with the same speedloader used by the O9 electromagnum. For those moments when 4 9mm bullets make the difference between YASD and survival.

- OCG-Leadworks T9, a heavyweight 9mm backup pistol made mostly of tungsten and other high density materials to reduce felt recoil while still being easily concealable.

- Reimagined the L39B as the OCG-Leadworks 923, which is closer to a Steyr TMP in dimensions than to a Beretta 93R but serves the same purpose, minus built-in accessories.

- In the grim darkness of the Cataclysm, diamond edged chainswords are real now also thanks to crowdfunding by not-Warhammer40k fans. They can replace electric carvers in a kitchen and while not folded 1000 times, cut a lot better than katanas.

- Atomic Irish coffee, which is the same as the default one, but made with atomic coffee instead of plain coffee or coffee syrup.

- Added Gunslinger of the Future profession, which starts with one OCG-L 45, one O9 Electromagnum, some ammo for both, some aluminum powder and knowledge plus skills to hand load ETC pistol ammo.

## New Fluff

- OmniCorp incorporated Leadworks when their original designs were still being prototyped. Take this with the grain of salt any fanon deserves.

- Renamed the O0238 submachinegun to 02020 so it is not inherently contradicting any retcon of mainline canon regarding timeline of the Cataclysm unless it gets even more retcons. Also Cyberpunk 2020.

- Redefined the vanilla description of plutonium cells in a more sci-fi way that doesn't contradict the explanation in the description for the self-charged 7.62mm electrothermal round, or the mad science to create smaller liquid core nanoreactors out of plutonium cells and complete disregard for radiation poisoning risks.
