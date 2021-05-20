### Weapon Type Differences
Every weapon damage are taken from `MHFU` and are calculated in this formulation:

* **Sword and Shields** - `atk` / 20 (+ attribute) = cut, 4 = bash
* **Greatswords** - `atk` / 30 (+ attribute) = cut, 8 = bash
* **Hammers** - `atk` / 30 + 2 (+ attribute) = bash
* **Lances** - `atk` / 22.5 (+ attribute) = stab, 10 = bash
* **Dual Blades** - `atk` / 15 (+ attribute) = cut
* **Light Bowguns** - `atk` / 15 = ranged, 6 = bash
* **Heavy Bowguns** - `atk` / 10 = ranged, 10 = bash

`atk` is the raw damage. Attribute damage types are added as physical damage...

* `elem` / 50 - Elemental damage types are fire, water, ice, electric and dragon.
* `abnm` / 75 - Abnormal damage types are poison, paralyze and sleep.

If there's more than two kinds of attribute in a weapon, their sum is halved.

**If you have a better weapon damage formulation, just tell me about it, cuz I believe mine is garbage :3**

### Bowgun Reload Speed
Reload speed greatly affects the player in the middle of a combat, where every turn is important to the gunner-type players. Lower reload speed value means faster reloading.
* **Very Slow** = 400
* **Slow** = 300
* **Normal** = 200
* **Fast** = 100
* **Very Fast** = 50

### Bowgun Capacity
Bowgun's clip size were based on the highest normal shot ammo capacity, and is halved for LBGs. Therefore, the highest possible capacity for HBGs is 12, while 6 for LBGs.

### Bowgun Ammunition
There's a wide variety of bowgun ammunitions in the actual game, but in CDDA, we have three types of ammo:

* **Normal Shot** - Basic ammunition; cheapest ammo and is focused to the raw damage of bowguns.
* **Pierce Shot** - Piercing ammunition; a lil' bit pricy and deals lesser damage, but ignores armor and is the most accurate ammo available.
* **Crag Shot** - Stunning ammunition; sold at high-price, but deals raw damage that stuns certain targets on impact. Its high recoil makes it unstable for rapid firing.

Every type of shots has level(lv) value affixed to them, which determines the quality and strength of the shot.