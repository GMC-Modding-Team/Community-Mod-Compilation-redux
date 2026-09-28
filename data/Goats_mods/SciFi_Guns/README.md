# Sci-Fi Guns and Future Tech for CDDA H release

Version: 0.9.6-H-release

This standalone mod adds **70 sci-fi guns** plus JSON-defined future-tech components, tools, passive armour, melee equipment, furniture, vehicle parts, a mobile research vehicle, recipes, loot groups, terrain, and construction for CDDA H release. It uses H-style `GUN`/`AMMO`/`MAGAZINE` item types and **no UPS dependency**.

See [Future-Tech-readme.md](Future-Tech-readme.md) for the detailed JSON-only expansion plan and implementation tracker.

## Included
- 70 total guns
- Existing plasma, photon/laser, electrical, and magnetic families
- 26 additional guns added in v0.8.0
- Existing custom ammo and magazines
- 9 future-tech component items, including singular fiber optics and a separate fiber-optic bundle
- 2 future-tech tools, 3 melee weapons, and 4 passive armour items
- 24 future-tech craft and uncraft recipe definitions, including reversible fiber-optic and vehicle-part recipes, and a mod-owned future-tech field cache
- 4 passive future-tech furniture definitions, 5 terrain definitions, and 8 construction recipes
- 2 craftable future-tech vehicle parts and a mobile research quad layout
- H-release compatible `pocket_data` magazine wells
- 32x32 mod tileset JSON (`mod_tileset.json`)
- 32x32 gun tilesheet (`scifi_guns_32.png`)

## New guns added in v0.8.0
- Plasma: plasma machine pistol, scout carbine, burst rifle, precision rifle, breacher, rotary cannon
- Photon/laser: photonic machine pistol, photonic PDW, photonic battle rifle, laser service rifle, beam sprayer, target pistol, designator carbine, heavy photon lance
- Electrical: arc machine pistol, storm pistol, arc carbine, tesla rifle, ion breacher, disruptor carbine
- Magnetic: needler pistol, coil SMG, gauss service rifle, rail carbine, accelerator rifle, compact mass driver

## Tileset
The mod includes a **mod tileset JSON** for 32x32 tiles.  It maps all 70 gun item IDs to the bundled sprite sheet.

## Notes
- The mod includes armour, melee weapons, furniture, terrain, construction, and JSON-defined vehicle parts in addition to guns.
- The mobile research quad uses standard vehicle-part behavior and is defined in a mod-owned vehicle group; it is not injected into main-game random-spawn tables.
- The tiles are bundled as a mod overlay and do not replace a full base tileset.
- The gun art is intended for use with common 32x32 tilesets such as Ultica-style sets.


## v0.8.1 update
- Added `scifi_ammo_mags_32.png`.
- Added tileset JSON mappings for all ammo and magazine item IDs.
- Ammo tiles mapped: 14.
- Magazine tiles mapped: 43.
- New v0.8.0 guns reuse existing compatible ammo/magazine families instead of adding disposable one-off magazines.


## v0.8.2 update
- Fixed H-release recipe `qualities` format.
- Converted array quality requirements like `[ "HAMMER", 2 ]` into `{ "id": "HAMMER", "level": 2 }`.


## v0.8.3 update
- Fixed H-release recipe difficulty range errors.
- Any recipe difficulty above 10 is now clamped to 10.
- Recipes changed: 3.


## Same-version bugfix: plasma projector ammo reference
- Kept version as `0.8.3-H-release`.
- Fixed invalid ammunition error: `swa_plasma_projector`.
- Corrected references to use `swa_plasma_projector_ammo`.


## Same-version bugfix: missing recipe component
- Kept version as `0.8.3-H-release`.
- Replaced invalid recipe component `aluminum` with valid item `scrap_aluminum`.
- Re-ran static missing-ID checks against the uploaded H-release game data.

## Same-version structure cleanup

The item JSON has been split into folders:

```text
items/
├─ guns/
│  ├─ base_guns.json
│  ├─ plasma_guns.json
│  ├─ photon_laser_guns.json
│  ├─ electrical_guns.json
│  └─ magnetic_guns.json
├─ ammo/
│  ├─ ammo.json
│  └─ ammo_types.json
└─ magazines/
   └─ magazines.json
```

The split is organizational only; item IDs, ammo IDs, magazine IDs, and recipes are preserved.

## Same-version tileset folder cleanup

Tilesheet PNGs are now stored in:

```text
tileset/
├─ scifi_guns_32.png
└─ scifi_ammo_mags_32.png
```

`mod_tileset.json` now points to those folder paths:

```json
"file": "tileset/scifi_guns_32.png"
"file": "tileset/scifi_ammo_mags_32.png"
```

## Same-version real item group and tile check update

Added `itemgroups/real_itemgroups.json` with strict separated spawn groups:

- gun groups contain guns only
- ammo groups contain loose ammo only
- magazine groups contain magazines only

Also checked `mod_tileset.json` mappings:

- `tileset/scifi_guns_32.png` maps gun IDs only
- `tileset/scifi_ammo_mags_32.png` maps ammo and magazine IDs only
