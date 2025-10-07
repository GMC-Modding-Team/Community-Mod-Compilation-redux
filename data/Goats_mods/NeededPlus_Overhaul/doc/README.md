
# NeededPlus: Overhaul v2 (No Mapgen)

A **modular**, JSON-only overhaul: deeper crafting, survival, vehicles, professions, traits, and gentle balance tweaks — **no mapgen** edits.

## Modules
- `crafting/materials`: resin → plant glue → hardened cloth, vinegar, fruit leather.
- `crafting/tools`: maintenance items (whetstone, oil), pro flashlight, pack frame (makeshift).
- `crafting/armor`: hardened cloth vest.
- `survival/foraging`: wild greens, wild tubers, portable drying rack.
- `survival/trapping`: simple snare.
- `vehicles/parts` + `vehicles/recipes`: rugged solar panel, cargo trailer hitch (craft-only).
- `professions`: Medic, Hiker, Rural Mechanic, Woodswoman.
- `traits`: Tool Familiarity, Packrat (minor), Calm Nerves.
- `balance`: alt recipes and autolearn boosts (no overrides).

## Install
Unzip into `data/mods/` as `NeededPlus_Overhaul_v2_NoMapgen/`. Enable the mod on your world.
Delete any module folder you don't want — they'll cleanly disable.

## Notes
- Everything uses `copy-from` or standalone JSON; safe to add/remove.
- No mapgen, no overmap specials, no terrain edits.
- If something conflicts, remove the single file/feature; the rest stands alone.
