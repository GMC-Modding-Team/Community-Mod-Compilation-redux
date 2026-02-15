Cannabis Overhaul Plus (CDDA 0.H stable-friendly)
-------------------------------------------------
Adds:
- 31 cannabis strains (THC-heavy, CBD-heavy, balanced) with plantable seeds
- Fresh buds (inedible) that can be dried on a smoking rack into strain-specific smokable buds
- THC/CBD "drug vitamins" for informational dosing readouts (values shown as mg)

Install:
1) Extract this folder into: data/mods/
2) Enable "Cannabis Overhaul Plus" when creating a new world (or add to an existing one at your own risk).

Notes:
- Seeds use 0.H's `seed_data` format (plant_name/fruit/grow).
- Fresh buds are SMOKABLE and define `smoking_result` -> dried buds (same mechanism used by meat/fish in 0.H).
- Dried buds require a smoking apparatus and a fire source (like vanilla `weed`).
- Item groups included for debugging/spawns:
  - cob_cannabis_overhaul_seeds
  - cob_cannabis_overhaul_buds

Strain rolling & disassembly:
- Disassemble any strain-specific dried buds (cob_weed_*) to get 1x matching raw strain cannabis (cob_raw_*).
- Craft a matching strain joint (cob_joint_*) from raw strain cannabis + rolling paper (or paper).
  Requires a fire source to smoke, but no smoking apparatus.
