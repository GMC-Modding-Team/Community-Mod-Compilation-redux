Cannabis Overhaul Plus
=====================

Adds strain-based cannabis with THC/CBD variation, strain-specific items, harvestable cannabis shrub terrain, and a full
processing chain (fresh -> dried -> trimmed -> strain joint). Includes improved THC vs CBD effects via custom effect_types.

Target: CDDA 0.H stable JSON

Core Features
-------------
Strains
- Each strain has:
  - Seeds:            cob_seed_<strain>
  - Fresh buds:       cob_cannabis_<strain>_fresh
  - Dried buds:       cob_weed_<strain>
  - Trimmed flower:   cob_trimmed_<strain>
  - Strain joint:     cob_joint_<strain>

Terrain plants (world shrubs)
- Each strain has a harvestable shrub terrain:
  - t_cob_cannabis_<strain>
  - t_cob_cannabis_<strain>_harvested
- These are TERRAIN plants. There is NO plant item (no cob_plant_*).

Strain Traits
-------------
Strains differ (JSON-side) in:
- Grow time (seed_data.grow): indica-leaning tends to be faster; sativa-leaning tends to be slower.
- Harvest yield (harvest tables): THC-dominant strains tend to yield more flower; CBD-dominant strains tend to drop more seeds.
- Harvest season (terrain): indica-leaning strains are harvestable in summer+autumn; others are autumn.

Effects (THC vs CBD)
--------------------
Cannabis now uses custom effect_types:
- cob_thc_high  : THC-heavy high (more hunger/thirst/sleepiness; coordination penalty at higher intensity; some pain relief)
- cob_cbd_calm  : CBD-heavy calm (more relaxation/sleepiness; pain relief; minimal impairment)

Balanced strains apply BOTH effects in smaller amounts.

Itemgroups
----------
Reusable itemgroups for distribution:
- cob_cannabis_overhaul_seeds
- cob_cannabis_overhaul_buds (fresh + dried)
- cob_cannabis_overhaul_fresh_buds
- cob_cannabis_overhaul_trimmed_flower
- cob_cannabis_overhaul_strain_joints

Mod Tileset
-----------
If you use a compatible graphical tileset, the mod includes mod_tileset mappings for all strain items + terrains.

Notes
-----
- If anything spawns invisible: check your tileset mapping includes that ID.

Credits
-------
Mod author: (TheGoatGod)