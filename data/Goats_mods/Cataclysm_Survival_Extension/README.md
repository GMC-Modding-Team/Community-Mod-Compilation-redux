# Cataclysm Survival Extension

Version: 0.6.5 for CDDA H release

A grounded, vanilla-style survival expansion for the base game. It focuses on the kind of equipment desperate survivors could plausibly make after the first weeks of the Cataclysm: scrap plates, padding rolls, improvised tools, ugly melee weapons, rough armor, carry rigs, field manuals, and profession starts.

## v0.3 expansion

- Adds a new intermediate scrapcraft material layer: salvage straps, patchwork padding, bent plate panels, lamellar strips, filter cores, tread patches, fastener tins, tarred cloth sheets, chain wraps, glassproof patches, splint boards, and quilted liners.
- Adds 20 more utility tools.
- Adds 25 more improvised melee weapons.
- Adds 32 more armor, clothing, and storage items.
- Adds 10 more field manuals.
- Adds 89 more craft recipes.
- Adds 8 more profession starts.
- Adds expanded item caches for materials, tools, weapons, armor, books, and new professions.

## Design limits

- No mapgen.
- No new monsters.
- No regional conversion.
- Includes an optional mod tileset; no external tileset dependency.
- Built conservatively for H-release JSON structure.

## v0.4 - Vanilla item-group integration

This version wires CSE content into existing H-release vanilla loot groups using same-id `item_group` patches with `copy-from` and `extend`.  The new file is:

- `itemgroups/vanilla_integration.json`

Integration targets include:

- common toolboxes, workshops, home hardware, construction, mechanics, tailoring, and survival tools
- evac shelter lockers and supply closets
- shelter loot
- survival kits and camping loot
- hardware, metal workshop, wood workshop, tailoring supplies, junk drawers, trash, and junkyard loot
- vanilla weapon pools and knife-shop loot
- survivor clothing/armor pools and general clothing
- medical gear and hospital medical item groups
- survival/manual/hardware/tailoring/SUS bookcase groups

Spawn rates are intentionally conservative so the mod feels like extra vanilla scavenging content rather than a loot flood.

## v0.5 - Larger survival expansion + deeper vanilla loot integration

This version adds a much larger vanilla-feeling layer on top of v0.4:

- new scrapcraft components for packs, masks, armor plates, straps, tarp panels, hinges, filter discs, and debris protection
- more improvised tools for window entry, rooftop scavenging, filtering, field sewing, cordage, patching, and rubble work
- more rough survivor weapons with reach, defensive doorway fighting, heavy debris breaking, and close-quarters scrap blades
- more armor, weather gear, masks, harnesses, storage rigs, packs, guards, and patched clothing
- more field manuals tied to survival, fabrication, tailoring, melee, first aid, and dodge
- more starting professions built around ruined-building survival roles
- deeper vanilla item group integration across domestic clutter, shelters, hardware, plumbing, mechanics, hiking, camping, clothing, fire/rescue, books, military/police-adjacent loot, and scavenging trash pools

Spawn rates remain intentionally conservative so the additions feel like extra Cataclysm-era scavenging finds rather than loot flooding.



## v0.6 - Custom mod tileset

This version adds a self-contained item tileset for the mod:

- `mod_tileset.json`
- `tileset/cse_items_32.png`
- `tileset/cse_tiles_manifest.json`

The sprite sheet maps every current custom CSE item ID:

- 65 tools
- 90 generic items / weapons / materials
- 86 armor, clothing, and storage items
- 26 books / field manuals

The art is 32x32, transparent-background, conservative, and vanilla-survival themed: scrap metal, cloth padding, rough leather straps, improvised blades, tools, masks, packs, armor, and field manuals.

The tileset is optional. If your active tileset supports mod tilesets, CSE items will use these sprites. If not, the mod still loads and falls back to normal game rendering.

## v0.6.1 Tile Fix

- Cleaned `tileset/cse_items_32.png` to remove semi-transparent black ground halos/shadows under sprites.
- Tile mappings are unchanged.


## v0.6.3 JSON cleanup

The JSON layout has been consolidated for easier editing and maintenance:

- `items/cse_items.json` contains all custom items, weapons, armor, tools, books, and scrapcraft materials.
- `recipes/cse_recipes.json` contains all custom craft recipes.
- `itemgroups/cse_itemgroups.json` contains all CSE cache groups plus vanilla item-group integration patches.
- `professions.json`, `mod_tileset.json`, and `tileset/` remain separate because CDDA and tileset maintenance are cleaner that way.

No item IDs, recipe results, profession starts, item-group IDs, or tile mappings were intentionally changed in this cleanup.


## v0.6.3 hotfix

- Fixed H-release item group parsing error caused by compact array entries inside `extend.entries`.
- Converted vanilla item group patch entries to explicit `{ "item": ..., "prob": ... }` objects.
- No item IDs, recipes, tiles, or gameplay values were intentionally changed.

## v0.6.4 - Vanilla item group patch style

Vanilla item-group integration patches now use the preferred H-release style:

```json
{
  "type": "item_group",
  "id": "example_group",
  "copy-from": "example_group",
  "extend": {
    "items": [
      { "item": "cse_example_item", "prob": 10 },
      { "group": "cse_example_cache", "prob": 15 }
    ]
  }
}
```

No gameplay content was intentionally changed. This only changes the vanilla loot integration patch format.


## v0.6.5 - Individual item-group counts

Updated item-group formatting so individual item entries use explicit count arrays, matching the preferred style:

```json
"extend": {
  "items": [
    { "item": "cse_example_item", "prob": 10, "count": [ 1, 1 ] }
  ]
}
```

- Added `count` arrays to individual CSE item entries in vanilla `copy-from` + `extend.items` patches.
- Added `count` arrays to CSE-owned cache entries where the entry is a custom CSE item and did not already use `count` or `charges`.
- Kept `{ "group": ..., "prob": ... }` entries as group entries without item counts.
- No IDs, recipes, tiles, or item stats were intentionally changed.


## v0.6.6 hotfix

- Confirmed vanilla same-id item-group patches use `copy-from` + `extend.items` only.
- Removed `subtype`/collection fields from vanilla integration patches inside the mod where present.
- CSE-owned item groups keep their required `subtype` declarations.
- Did not remove vanilla integration patches unless duplicated inside the mod.
