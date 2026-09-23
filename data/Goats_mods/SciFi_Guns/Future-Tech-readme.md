# Future Technology mod - Sci-Fi Guns Pack

Use the `home` key to get to the top.

Version: `0.9.0-H-release`

This standalone mod adds future-tech weapons and JSON-defined support equipment to the Cataclysm: Dark Days Ahead H release. It includes plasma, photon, laser, electrical, magnetic, coil, gauss, and rail weapons with custom ammunition and magazines, plus mod-owned components, tools, passive armour, melee equipment, recipes, and loot groups.

The current release is data-only. It adds no custom C++ behaviour, no new main-game definitions, no furniture or terrain, no vehicles, and no UPS dependency.

# Table of contents

* [To-do](#to-do)
* [Future Technology Sources](#future-technology-sources)
* [Features](#features)
* [Future-Tech Expansion Plan](#future-tech-expansion-plan)
* [Main-Game Content Boundary](#main-game-content-boundary)
* [Vanilla-Code](#vanilla-code)
* [Items](#items)
  * [Weapons](#weapons)
    * [Plasma](#plasma)
    * [Photon and Laser](#photon-and-laser)
    * [Electrical](#electrical)
    * [Magnetic](#magnetic)
  * [Ammo](#ammo)
  * [Magazines](#magazines)
* [Furniture and Terrain](#furniture-and-terrain)
* [Construction](#construction)
* [Vehicles](#vehicles)
* [Recipes](#recipes)
  * [Weapon Recipes](#weapon-recipes)
  * [Ammo Recipes](#ammo-recipes)
* [Item Groups](#item-groups)
* [Tileset](#tileset)
* [Compatibility and Limitations](#compatibility-and-limitations)
* [Changelog](#changelog)

# To-do

**Head-Category -** [To-do](#to-do)

*Priority Todos:*
---

```markdown
- [x] Add plasma weapons
- [x] Add photon and laser weapons
- [x] Add electrical weapons
- [x] Add magnetic, coil, gauss, and rail weapons
- [x] Add custom ammunition types
- [x] Add compatible magazines and drums
- [x] Add H-release `GUN`, `AMMO`, and `MAGAZINE` item types
- [x] Add craft recipes for selected weapons and all custom ammunition
- [x] Add separated item groups for guns, ammunition, and magazines
- [x] Add 32x32 gun, ammunition, and magazine tiles
- [x] Add future-tech armour
- [x] Add future-tech tools and melee weapons
- [x] Add JSON-defined future-tech components and capacitor recipes
- [x] Add mod-owned future-tech equipment and field-cache groups
- [ ] Add JSON-defined furniture, terrain, and construction
- [ ] Add JSON-defined vehicle parts and layouts using supported fields
- [ ] Add and test EOCs only where existing H-release conditions and effects support them
- [ ] Check every new ID against the main-game JSON before adding it
- [ ] Keep all future-tech definitions inside the mod's `swa_` namespace
```

# Future Technology Sources

**Head-Category -** [Future Technology Sources](#future-technology-sources)

*Current mod data:*

[Mod metadata](modinfo.json)\
[Gun definitions](items/guns)\
[Ammunition definitions](items/ammo)\
[Magazine definitions](items/magazines)\
[Crafting recipes](recipes/swa_recipes.json)\
[Spawn groups](itemgroups)\
[Tileset mappings](tileset/mod_tileset.json)\
[Future-tech components](items/future_tech_components.json)\
[Future-tech equipment](items/future_tech_equipment.json)\
[Future-tech recipes](recipes/future_tech_recipes.json)\
[Future-tech item groups](itemgroups/future_tech_itemgroups.json)

*Implementation notes:*

- Weapon families are split into separate JSON files for easier maintenance.
- Ammunition is defined independently from guns and magazines.
- The `swa_` prefix is used for this mod's item and ammunition IDs.
- The design uses reusable ammunition families instead of disposable one-off ammunition for every gun.

# Features

**Head-Category -** [Features](#features)

```markdown
- [x] 70 future-tech guns
- [x] 14 custom ammunition types
- [x] 43 custom magazines, drums, packs, cassettes, and clips
- [x] 8 mod-owned future-tech component items
- [x] 2 future-tech tools, 3 melee weapons, and 4 passive armour items
- [x] 66 recipes in total
- [x] Plasma, photon, laser, electrical, magnetic, coil, gauss, and rail technology
- [x] Direct H-release item types: `GUN`, `AMMO`, and `MAGAZINE`
- [x] No UPS dependency
- [x] Separate spawn groups for guns, ammunition, magazines, and future-tech equipment
- [x] 32x32 tiles for all guns, ammunition, and magazines
```

# Future-Tech Expansion Plan

**Head-Category -** [Future-Tech Expansion Plan](#future-tech-expansion-plan)

This expansion is limited to content that can be represented by the existing Cataclysm: Dark Days Ahead H-release JSON schemas. The plan uses item definitions, recipes, item groups, EOCs, tileset mappings, and other data files already supported by the game.

Anything marked **planned** in this section is a data-content target and is not part of the current `0.9.0-H-release` content yet. The implemented component, equipment, recipe, and item-group files are listed in the Features and Sources sections.

## JSON-only scope

The expansion can add or organize data in these areas:

```markdown
- [ ] Item definitions such as `GUN`, `AMMO`, `MAGAZINE`, tools, clothing, armour, and ordinary components
- [ ] Recipes with existing skills, qualities, tools, components, time, difficulty, and outputs
- [ ] Item groups for civilian, military, research, laboratory, and specialist loot
- [ ] EOCs using conditions and effects already accepted by the H release
- [ ] Furniture and terrain definitions using existing furniture and terrain fields
- [ ] Construction definitions that place supported furniture or terrain
- [ ] Vehicle definitions and vehicle parts using existing vehicle JSON fields
- [ ] Mod tileset mappings and new PNG sprite sheets
- [ ] Localisation strings and item descriptions supported by the data format
```

The expansion will not add new C++ behaviour, new UI, new skills, new AI, or new game mechanics. A planned feature is included only when it can use a field or content type already accepted by the H release.

## Main-Game Content Boundary

The future-tech expansion is an add-on to the main game, not a replacement or duplicate of main-game content.

```markdown
- [ ] Give every new item, recipe, EOC, item group, furniture, terrain, construction, vehicle, and vehicle part a unique mod-owned ID
- [ ] Use the `swa_` prefix for new IDs wherever the JSON type allows it
- [ ] Check new IDs against the main-game JSON before adding them
- [ ] Do not copy vanilla item definitions into the mod
- [ ] Do not redefine, replace, or override vanilla items
- [ ] Do not add a second version of an existing vanilla battery, circuit, tool, weapon, clothing item, or material
- [ ] Use existing main-game items as recipe components, tools, qualities, or skill requirements when they already fill the role
- [ ] Keep new loot groups mod-owned and separate from main-game group definitions
- [ ] Only append `swa_` items to a main-game group when H-release JSON explicitly supports the operation and the integration is tested
- [ ] Do not edit files in the main game's `data/json` content as part of this expansion
```

Main-game content may be referenced, but it is not counted as part of the future-tech expansion. For example, a recipe may require a vanilla soldering iron, copper wire, circuit, battery, electronics skill, or tool quality; the mod must not create duplicate versions of those objects.

Before committing a new JSON file, perform a duplicate-ID check against the base game and the other loaded mods. If an intended name already exists, the expansion must either use the existing ID or choose a clearly namespaced `swa_` ID with a different purpose.

## Data-driven progression

The technology progression will be represented through recipe requirements, item-group rarity, and tested EOCs—not through a new research system or a custom unlock menu.

```markdown
- [ ] Early equipment uses common scrap, wire, plastic, glass, batteries, and simple circuits
- [ ] Mid-tier equipment requires higher electronics and fabrication skills
- [ ] Military equipment uses advanced components, amplifiers, cooling parts, and specialist tools
- [ ] Experimental equipment uses rare components, high recipe difficulty, long crafting time, and restricted item groups
- [ ] Item groups keep complete high-tier weapons uncommon
- [ ] Recipe requirements provide the progression gate
- [ ] Existing skills and qualities provide the crafting gate
- [ ] EOCs are added only when an existing condition/effect expresses the intended behaviour
```

### Stage 1 - Salvaged Electronics

This stage adds ordinary future-tech parts and low-tier equipment that can be crafted with existing skills and tools.

```markdown
- [ ] Salvaged circuit board - ordinary component item
- [ ] Damaged capacitor - component item
- [ ] Emitter lens - glass and electronics component
- [ ] Power-cell casing - component or magazine component
- [ ] Sensor module - electronics component
- [ ] Signal processor - advanced electronics component
- [ ] Portable diagnostic tool - tool item using existing tool fields
- [ ] Salvaged energy pistol - low-tier `GUN` item
- [ ] Basic energy magazine - `MAGAZINE` item
```

### Stage 2 - Field Equipment

This stage adds practical equipment using existing item types, charges, ammunition, and recipes. It does not create a new charging mechanic.

```markdown
- [ ] Rechargeable-cell item definitions using supported charge fields
- [ ] Capacitor magazines for existing weapon families
- [ ] Portable electronics tool
- [ ] Field sensor tool using an existing supported tool action
- [ ] Low-tier energy-resistant clothing
- [ ] Replacement emitter and capacitor recipes
- [ ] Field equipment item groups
```

### Stage 3 - Military and Research Equipment

This stage expands the current weapon families and adds more demanding recipes and loot groups.

```markdown
- [ ] Additional plasma, photon, laser, electrical, gauss, and rail `GUN` items
- [ ] Military magazines and ammunition containers
- [ ] Advanced targeting optics as ordinary tool or attachment items where supported
- [ ] Thermal-resistant clothing using standard clothing fields
- [ ] Research and military item groups
- [ ] High-skill recipes using existing electronics and fabrication requirements
```

### Stage 4 - Experimental Equipment

The final stage is limited to powerful but ordinary JSON items. It cannot introduce new projectile physics, custom interactions, or special behaviour that the game does not already support.

```markdown
- [ ] Very high-difficulty experimental `GUN` items
- [ ] Rare ammunition and magazine definitions
- [ ] Prototype armour with supported protection and encumbrance fields
- [ ] Experimental tools using existing tool actions
- [ ] Rare prototype item groups
- [ ] New sprites and descriptions for every experimental item
```

## Planned item expansion

### Weapons

New weapons will use the existing H-release `GUN` schema. Their behaviour must come from fields and effects already supported by the game.

```markdown
- [ ] Plasma sidearms, carbines, rifles, and heavy weapons
- [ ] Photon pistols, repeaters, carbines, and precision weapons
- [ ] Arc pistols, shock weapons, disruptors, and electrical rifles
- [ ] Gauss pistols, coil weapons, rail rifles, and mass drivers
- [ ] Breaching and industrial energy weapons
- [ ] Training and low-power variants
- [ ] Specialist weapons with narrow ammunition compatibility
```

Each new gun must have:

```markdown
- [ ] A unique item ID with the `swa_` prefix
- [ ] A valid name, description, weight, volume, price, and category
- [ ] A supported ammunition type
- [ ] A compatible magazine or internal capacity definition
- [ ] Valid damage, dispersion, range, recoil, and firing mode fields
- [ ] A recipe or an explicit loot-only decision
- [ ] An item-group entry if it should spawn naturally
- [ ] A tileset mapping if artwork is available
```

### Ammunition and magazines

Ammunition will remain data-driven and compatible with the existing gun families.

```markdown
- [ ] Add new `AMMO` definitions only for ammunition with a real supported use
- [ ] Add `MAGAZINE` definitions for guns that need dedicated containers
- [ ] Reuse existing ammunition families when a new item does not need a new type
- [ ] Add recipes for ammunition and magazines where components are available
- [ ] Keep ammunition, guns, and magazines in separate item groups
- [ ] Add sprites and tileset mappings for new ammunition and magazines
```

Ammunition can use existing charge counts, damage values, casing fields, flags, and effects. The plan does not include a new dynamic battery, heat, overcharge, or power-grid mechanic.

### Tools and components

Tools and components will use ordinary JSON item definitions and existing tool behaviour.

```markdown
- [ ] Capacitors and capacitor casings
- [ ] Emitters and emitter lenses
- [ ] Coils and magnetic assemblies
- [ ] Power-cell casings
- [ ] Sensor modules
- [ ] Targeting circuits
- [ ] Cooling components as ordinary recipe components
- [ ] Electronics repair tools using existing tool actions
- [ ] Laser cutting tools only where an existing tool action supports them
- [ ] Scanner items only where an existing tool action supports them
```

A new item will not claim to scan, repair, cut, charge, shield, camouflage, or communicate unless the base game already exposes that action to JSON.

### Clothing and armour

Armour is suitable for JSON when it uses the normal clothing and armour fields.

```markdown
- [ ] Insulated undersuit
- [ ] Energy-resistant vest
- [ ] Sensor hood
- [ ] Electronics harness
- [ ] Future-tech helmet
- [ ] Reinforced gloves and boots
- [ ] Modular tactical armour
- [ ] Prototype protective suit
```

The armour plan is limited to supported material, coverage, protection, storage, encumbrance, warmth, flags, and other existing item fields. It does not include active energy shields, automatic camouflage, powered exoskeleton behaviour, or new damage systems.

### Melee weapons

Future-tech melee items can be added as normal weapon definitions.

```markdown
- [ ] Powered baton using an existing melee damage model
- [ ] Shock prod using an existing electrical effect if supported
- [ ] Plasma cutting blade using supported damage and material fields
- [ ] Magnetic breaching hammer using supported melee fields
- [ ] Monomolecular utility knife using an existing cutting tool or weapon model
```

These items will not add a new powered-melee system. If a special effect is not available through JSON, the item will use ordinary damage, flags, qualities, and recipes instead.

## EOCs

EOCs are allowed only when the H-release JSON schema already provides the required condition and effect.

```markdown
- [ ] Use an EOC to trigger an existing supported effect from an item use
- [ ] Use existing conditions to check a supported item, flag, character state, time, or location
- [ ] Use existing effects to apply supported effects, transform supported items, or run supported data actions
- [ ] Give every EOC a unique ID and a clear description
- [ ] Test the condition and the effect separately in-game
- [ ] Test false-condition behaviour so the EOC does not fire unintentionally
- [ ] Keep EOCs small and single-purpose
- [ ] Remove any EOC that needs a new engine-side effect or custom action
```

EOCs will not be used to create a new power grid, new AI, a research tree, an active shield system, custom UI, or a new weapon mechanic. If an EOC cannot make the intended feature work reliably using existing H-release conditions and effects, that feature will be removed from the plan.

## Recipes

Recipes provide the main JSON-compatible progression system.

```markdown
- [ ] Weapon assembly recipes
- [ ] Ammunition loading recipes
- [ ] Magazine assembly recipes
- [ ] Component fabrication recipes
- [ ] Clothing and armour recipes
- [ ] Tool assembly recipes
- [ ] Construction recipes for supported furniture and terrain
- [ ] Vehicle-part recipes
```

Every recipe should use only existing recipe fields:

```markdown
- [ ] Result item
- [ ] Crafting category and subcategory
- [ ] Skill and difficulty
- [ ] Crafting time
- [ ] Tool qualities
- [ ] Required tools
- [ ] Components
- [ ] Optional proficiencies already supported by the game
```

Recipe progression will be created through skill levels, tool qualities, components, time, difficulty, and recipe availability. There will be no custom recipe-unlock terminal or data-card system.

## Furniture and terrain

Furniture and terrain can be added only as definitions using fields already accepted by the H release.

```markdown
- [ ] Future-tech storage cabinet
- [ ] Ammunition locker
- [ ] Electronics workbench as a static furniture definition
- [ ] Laboratory floor and wall
- [ ] Reinforced laboratory door
- [ ] Cable and conduit terrain
- [ ] Research-room decorative furniture
- [ ] Secure equipment rack
```

These objects may provide supported storage, movement, obstruction, examination, or crafting requirements when the base game supports those fields. They will not introduce a custom workstation interface, a power grid, a charging interaction, or a new furniture action.

## Construction

Construction expansion will use ordinary construction entries that create supported terrain or furniture.

```markdown
- [ ] Reinforced laboratory wall
- [ ] Reinforced laboratory door
- [ ] Secure equipment floor
- [ ] Cable conduit terrain
- [ ] Equipment rack
- [ ] Ammunition locker
- [ ] Laboratory storage cabinet
```

Construction recipes will be gated by existing skills, tools, qualities, time, and components. They will not create electricity networks or require a new construction system.

## Vehicles and vehicle parts

Vehicle content is possible when it uses existing vehicle JSON definitions and part fields.

```markdown
- [ ] Battery rack vehicle part
- [ ] Solar panel vehicle part using existing vehicle power fields
- [ ] Capacitor storage vehicle part
- [ ] Research equipment vehicle part
- [ ] Vehicle-mounted laser using an existing vehicle weapon model
- [ ] Vehicle-mounted coil or rail weapon using supported vehicle fields
- [ ] Armoured research vehicle layout
- [ ] Mobile storage and ammunition vehicle layout
```

The vehicle expansion will not include autonomous drones, remote control AI, new vehicle power behaviour, or new vehicle weapon mechanics. It will use existing vehicle engines, batteries, solar panels, cargo, armour, turrets, and weapon fields.

## Item groups and loot

Item groups are fully data-driven and will be used to distribute the expansion.

```markdown
- [ ] Civilian electronics group
- [ ] Industrial electronics group
- [ ] Laboratory components group
- [ ] Military energy weapons group
- [ ] Military ammunition group
- [ ] Research prototype group
- [ ] Future-tech clothing group
- [ ] Future-tech tools group
- [ ] Vehicle technology group
- [ ] Rare experimental group
```

Distribution rules:

```markdown
- [ ] Common components appear in appropriate civilian and industrial groups
- [ ] Complete weapons remain less common than components
- [ ] Military weapons and magazines use military groups
- [ ] Research items use laboratory and science groups
- [ ] Experimental items use rare or specialist groups
- [ ] Guns, ammunition, and magazines remain separated
- [ ] Every group uses valid existing item IDs
```

## Tileset and localisation

Every new visible item should receive data support for presentation.

```markdown
- [ ] Add a sprite for each new gun
- [ ] Add sprites for new ammunition and magazines
- [ ] Add sprites for clothing, tools, furniture, and terrain where needed
- [ ] Add valid `mod_tileset` mappings
- [ ] Keep sprite dimensions compatible with the selected tileset
- [ ] Add names and descriptions through supported JSON localisation fields
```

## JSON-only implementation order

```markdown
- [ ] Phase 1: Add component, ammunition, magazine, and item definitions
- [ ] Phase 2: Add recipes with valid skills, qualities, tools, and components
- [ ] Phase 3: Add clothing, armour, tools, melee items, and tested EOCs
- [ ] Phase 4: Add item groups and check every referenced ID
- [ ] Phase 5: Add furniture, terrain, and construction definitions
- [ ] Phase 6: Add vehicle parts and vehicle layouts using existing fields
- [ ] Phase 7: Add tileset mappings and localisation
- [ ] Phase 8: Validate all JSON and remove unsupported or orphaned content
```

## Explicitly out of scope

The following are not part of the JSON-only expansion:

```markdown
- [ ] Dynamic power grids
- [ ] Custom charging-station behaviour
- [ ] Weapon heat, overheat, or cooling mechanics not already supported
- [ ] Active energy shields
- [ ] Automatic camouflage
- [ ] Autonomous drones or new AI behaviour
- [ ] New skills, stats, needs, or UI screens
- [ ] Recipe unlocking through terminals, data cards, or research trees
- [ ] Custom quests or scripted missions
- [ ] New projectile physics or damage types
- [ ] New interaction menus or C++ item actions
```

# Vanilla-Code
# Vanilla-Code

**Head-Category -** [Vanilla-Code](#vanilla-code)

The mod does not replace vanilla files. It uses the H-release item and recipe formats and adds its own definitions through the normal mod-loading system.

```markdown
- [x] Use H-release `GUN` item definitions
- [x] Use H-release `AMMO` item definitions
- [x] Use H-release `MAGAZINE` item definitions
- [x] Use H-release `pocket_data` magazine wells
- [x] Use H-release recipe quality objects
- [x] Keep recipe difficulty at or below 10
- [x] Remove the old UPS dependency
- [x] Correct the plasma projector ammunition reference
- [x] Use `scrap_aluminum` instead of the invalid `aluminum` component
```

# Items

**Head-Category -** [Items](#items)

*All Sub Categories:*

[Weapons](#weapons)\
[Ammo](#ammo)\
[Magazines](#magazines)

## Weapons

**Head-Category -** [Items](#items)\
**Sub-Category -** [Weapons](#weapons)

The mod contains 70 guns. The IDs below are the IDs used by the JSON files.

### Plasma

**Source:** [plasma_guns.json](items/guns/plasma_guns.json)

```markdown
- [x] PCX-24 plasma carbine - `swa_plasma_carbine`
- [x] PPP-12 plasma pistol - `swa_plasma_pistol`
- [x] PRX-36 plasma repeater - `swa_plasma_repeater`
- [x] PLR-10 plasma lance rifle - `swa_plasma_lance_rifle`
- [x] HPX-4 heavy plasma projector - `swa_plasma_projector`
- [x] PDM-5 plasma derringer - `swa_plasma_derringer`
- [x] PCH-9 plasma hand cannon - `swa_plasma_hand_cannon`
- [x] PSS-18 plasma scattergun - `swa_plasma_scattergun`
- [x] PSR-50 plasma support rifle - `swa_plasma_support_rifle`
- [x] ELC-2 electrolaser pistol - `swa_electrolaser_pistol`
- [x] PPM-18 plasma machine pistol - `swa_plasma_machine_pistol`
- [x] PSC-20 plasma scout carbine - `swa_plasma_scout_carbine`
- [x] PBR-40 plasma burst rifle - `swa_plasma_burst_rifle`
- [x] PPR-48 plasma precision rifle - `swa_plasma_precision_rifle`
- [x] PBG-16 plasma breacher - `swa_plasma_breacher`
- [x] PRC-88 plasma rotary cannon - `swa_plasma_rotary_cannon`
```

### Photon and Laser

**Source:** [photon_laser_guns.json](items/guns/photon_laser_guns.json)

```markdown
- [x] LXR-30 photonic rifle - `swa_photon_rifle`
- [x] LXP-3 photonic pistol - `swa_photon_pistol`
- [x] LXC-12 photonic carbine - `swa_photon_carbine`
- [x] LXM-90 heavy photonic cannon - `swa_photon_cannon`
- [x] LHD-2 laser holdout pistol - `swa_laser_holdout_pistol`
- [x] LSP-8 laser sidearm - `swa_laser_sidearm`
- [x] LRP-14 pulse laser repeater - `swa_laser_repeater`
- [x] LSG-15 prismatic scatter laser - `swa_prism_scatter_laser`
- [x] LMR-34 laser marksman rifle - `swa_laser_marksman`
- [x] LUV-21 ultraviolet laser rifle - `swa_uv_laser_rifle`
- [x] LIR-17 infrared laser carbine - `swa_ir_laser_carbine`
- [x] LSW-55 laser squad weapon - `swa_laser_lmg`
- [x] ICL-7 industrial cutting laser - `swa_industrial_cutting_laser`
- [x] LXS-66 excimer sniper laser - `swa_excimer_sniper_laser`
- [x] HBL-99 heavy beam laser - `swa_heavy_beam_laser`
- [x] LMP-6 photonic machine pistol - `swa_photon_machine_pistol`
- [x] LPD-11 photonic PDW - `swa_photon_pdw`
- [x] LBR-28 photonic battle rifle - `swa_photon_battle_rifle`
- [x] LSR-24 laser service rifle - `swa_photon_service_rifle`
- [x] LBS-20 beam sprayer - `swa_photon_beam_sprayer`
- [x] LTP-9 target laser pistol - `swa_photon_target_pistol`
- [x] LDR-12 laser designator carbine - `swa_photon_designator`
- [x] HPL-77 heavy photon lance - `swa_heavy_photon_lance`
```

### Electrical

**Source:** [electrical_guns.json](items/guns/electrical_guns.json)

```markdown
- [x] AEP-9 arc pistol - `swa_arc_pistol`
- [x] MCR-18 coil rifle - `swa_coil_rifle`
- [x] ESP-4 stun pistol - `swa_stun_pistol`
- [x] AER-6 arc revolver - `swa_arc_revolver`
- [x] ARX-22 arc rifle - `swa_arc_rifle`
- [x] CCX-9 chain caster - `swa_chain_caster`
- [x] EDR-13 pulse disruptor - `swa_emp_disruptor`
- [x] SLG-40 storm gun - `swa_storm_lmg`
- [x] MCK-21 coil carbine - `swa_coil_carbine`
- [x] MDX-80 mass driver - `swa_mass_driver`
- [x] TRX-18 thunder rifle - `swa_thunder_rifle`
- [x] ESH-12 shock scatterer - `swa_shock_scatterer`
- [x] MCS-16 coil scattergun - `swa_coil_scattergun`
- [x] AMP-5 arc machine pistol - `swa_arc_machine_pistol`
- [x] STP-3 storm pistol - `swa_storm_pistol`
- [x] ARC-19 arc carbine - `swa_arc_carbine`
- [x] TSR-31 tesla rifle - `swa_tesla_rifle`
- [x] IBR-14 ion breacher - `swa_ion_breacher`
- [x] DCR-22 disruptor carbine - `swa_disruptor_carbine`
- [x] GSR-27 gauss service rifle - `swa_gauss_rifle`
- [x] RCB-25 rail carbine - `swa_rail_carbine`
```

### Magnetic

**Source:** [magnetic_guns.json](items/guns/magnetic_guns.json)

```markdown
- [x] MGP-7 gauss pistol - `swa_gauss_pistol`
- [x] MGS-11 gauss PDW - `swa_gauss_pdw`
- [x] MMR-33 gauss marksman rifle - `swa_gauss_marksman_rifle`
- [x] MRR-42 rail rifle - `swa_rail_rifle`
- [x] MFS-14 magnetic flechette SMG - `swa_flechette_smg`
- [x] MAR-60 rail antimateriel rifle - `swa_rail_antimateriel`
- [x] NDP-4 needler pistol - `swa_needler_pistol`
- [x] CSL-9 coil SMG - `swa_coil_smg`
- [x] AXR-44 accelerator rifle - `swa_accelerator_rifle`
- [x] CMD-62 compact mass driver - `swa_compact_mass_driver`
```

## Ammo

**Head-Category -** [Items](#items)\
**Sub-Category -** [Ammo](#ammo)

**Source:** [ammo.json](items/ammo/ammo.json)

```markdown
- [x] Arc capacitor cells - `swa_arc_cell` - 40 charges - `swa_arc`
- [x] Plasma charge cells - `swa_plasma_cell` - 30 charges - `swa_plasma`
- [x] Ferromagnetic slugs - `swa_ferroslug` - 50 charges - `swa_ferro`
- [x] Photonic charge cells - `swa_photon_cell` - 35 charges - `swa_photon`
- [x] Compact plasma microcells - `swa_plasma_microcell` - 40 charges - `swa_plasma_micro`
- [x] Plasma lance cells - `swa_plasma_lance_cell` - 20 charges - `swa_plasma_lance`
- [x] Plasma projector canisters - `swa_plasma_projector_canister` - 8 charges - `swa_plasma_projector_ammo`
- [x] Shock capacitor cells - `swa_shock_capacitor` - 32 charges - `swa_shock`
- [x] Ion charge cells - `swa_ion_cell` - 28 charges - `swa_ion`
- [x] Storm capacitor banks - `swa_storm_capacitor` - 12 charges - `swa_storm`
- [x] Disruptor induction cells - `swa_disruptor_cell` - 18 charges - `swa_disruptor`
- [x] Micro ferromagnetic needles - `swa_micro_ferroslug` - 80 charges - `swa_microferro`
- [x] Rail sabot penetrators - `swa_rail_sabot` - 30 charges - `swa_rail_sabot_ammo`
- [x] Heavy mass-driver slugs - `swa_heavy_mass_slug` - 8 charges - `swa_heavyferro`
```

## Magazines

**Head-Category -** [Items](#items)\
**Sub-Category -** [Magazines](#magazines)

**Source:** [magazines.json](items/magazines/magazines.json)

*Plasma magazines:*

```markdown
- [x] Plasma carbine cell magazine - `swa_plasma_carbine_mag`
- [x] Plasma carbine drum - `swa_plasma_carbine_drum`
- [x] Plasma pistol cell magazine - `swa_plasma_pistol_mag`
- [x] Plasma repeater cell magazine - `swa_plasma_repeater_mag`
- [x] Plasma lance cell magazine - `swa_plasma_lance_mag`
- [x] Plasma projector canister rack - `swa_plasma_projector_canister_pack`
- [x] Plasma scattergun cell magazine - `swa_plasma_scatter_mag`
- [x] Plasma hand-cannon lance magazine - `swa_plasma_hand_cannon_mag`
- [x] Plasma support rifle cell box - `swa_plasma_support_pack`
```

*Electrical magazines:*

```markdown
- [x] Arc pistol capacitor magazine - `swa_arc_pistol_mag`
- [x] Shock pistol capacitor magazine - `swa_shock_pistol_mag`
- [x] Arc rifle ion magazine - `swa_arc_rifle_mag`
- [x] Arc rifle capacitor drum - `swa_arc_rifle_drum`
- [x] Storm capacitor pack - `swa_storm_capacitor_pack`
- [x] Disruptor induction magazine - `swa_disruptor_mag`
- [x] Thunder rifle ion magazine - `swa_thunder_rifle_mag`
- [x] Shock scatterer capacitor magazine - `swa_shock_scatterer_mag`
- [x] Electrolaser capacitor magazine - `swa_electrolaser_mag`
```

*Magnetic magazines:*

```markdown
- [x] Coil rifle slug magazine - `swa_coil_rifle_mag`
- [x] Gauss pistol needle magazine - `swa_gauss_pistol_mag`
- [x] Gauss PDW needle magazine - `swa_gauss_pdw_mag`
- [x] Coil carbine slug magazine - `swa_coil_carbine_mag`
- [x] Rail rifle sabot magazine - `swa_rail_rifle_mag`
- [x] Rail rifle sabot drum - `swa_rail_rifle_drum`
- [x] Mass-driver slug clip - `swa_mass_driver_clip`
- [x] Magnetic flechette drum - `swa_flechette_smg_mag`
- [x] Coil scattergun slug magazine - `swa_coil_shotgun_mag`
- [x] Rail antimateriel sabot magazine - `swa_rail_antimateriel_mag`
```

*Photon and laser magazines:*

```markdown
- [x] Photonic rifle cell magazine - `swa_photon_rifle_mag`
- [x] Photonic pistol cell magazine - `swa_photon_pistol_mag`
- [x] Photonic carbine cell magazine - `swa_photon_carbine_mag`
- [x] Heavy photonic cannon cassette - `swa_photon_cannon_cassette`
- [x] Holdout laser cell magazine - `swa_laser_holdout_mag`
- [x] Laser sidearm cell magazine - `swa_laser_sidearm_mag`
- [x] Laser repeater cell magazine - `swa_laser_repeater_mag`
- [x] Laser repeater drum - `swa_laser_repeater_drum`
- [x] Prismatic scatter-laser cassette - `swa_prism_scatter_cassette`
- [x] Precision laser cell magazine - `swa_laser_marksman_mag`
- [x] Ultraviolet laser magazine - `swa_uv_laser_mag`
- [x] Laser squad-weapon cell box - `swa_laser_lmg_box`
- [x] Cutting-laser power cassette - `swa_cutting_laser_cassette`
- [x] Excimer sniper laser cell - `swa_excimer_sniper_cell`
- [x] Heavy beam-laser cassette - `swa_heavy_beam_cassette`
```

# Furniture and Terrain

**Head-Category -** [Furniture and Terrain](#furniture-and-terrain)

The current release adds no furniture or terrain.

```markdown
- [ ] Future-tech storage cabinet
- [ ] Ammunition locker
- [ ] Electronics workbench as a static furniture definition
- [ ] Laboratory containment wall or display furniture
- [ ] Research terminal prop as static furniture only
```

# Construction

**Head-Category -** [Construction](#construction)

The current release adds no construction pieces. Future construction can provide JSON-defined structures, storage, and supported furniture or terrain.

```markdown
- [ ] Buildable future-tech storage area
- [ ] Buildable laboratory walls and doors
- [ ] Buildable equipment racks and ammunition lockers
```

# Vehicles

**Head-Category -** [Vehicles](#vehicles)

The current release adds no vehicles or vehicle parts.

```markdown
- [ ] Add a scout vehicle layout using supported vehicle JSON
- [ ] Add magnetic or plasma vehicle weapons where supported
- [ ] Add vehicle battery, solar, armour, cargo, and weapon parts using existing fields
```

# Recipes

**Head-Category -** [Recipes](#recipes)

The recipe files contain 66 recipes: 35 existing weapon recipes, 14 ammunition recipes, and 17 future-tech component and equipment recipes. The new recipes use existing fabrication and electronics skills, soldering iron or toolset qualities, and vanilla metal, wire, plastic, glass, amplifier, circuit, and pipe components.

## Weapon Recipes

**Head-Category -** [Recipes](#recipes)\
**Sub-Category -** [Weapon Recipes](#weapon-recipes)

**Source:** [swa_recipes.json](recipes/swa_recipes.json)

*Electrical weapons:*

```markdown
- [x] Arc rifle
- [x] Chain caster
- [x] Coil carbine
- [x] Coil scattergun
- [x] Pulse disruptor
- [x] Mass driver
- [x] Shock scatterer
- [x] Stun pistol
- [x] Thunder rifle
```

*Magnetic weapons:*

```markdown
- [x] Magnetic flechette SMG
- [x] Gauss PDW
- [x] Gauss pistol
- [x] Rail antimateriel rifle
- [x] Rail rifle
```

*Photon and laser weapons:*

```markdown
- [x] Excimer sniper laser
- [x] Heavy beam laser
- [x] Industrial cutting laser
- [x] Infrared laser carbine
- [x] Laser holdout pistol
- [x] Laser squad weapon
- [x] Laser marksman rifle
- [x] Pulse laser repeater
- [x] Laser sidearm
- [x] Heavy photonic cannon
- [x] Photonic carbine
- [x] Photonic pistol
- [x] Prismatic scatter laser
- [x] Ultraviolet laser rifle
```

*Plasma and hybrid weapons:*

```markdown
- [x] Electrolaser pistol
- [x] Plasma derringer
- [x] Plasma hand cannon
- [x] Plasma pistol
- [x] Plasma repeater
- [x] Plasma scattergun
- [x] Plasma support rifle
```

## Ammo Recipes

**Head-Category -** [Recipes](#recipes)\
**Sub-Category -** [Ammo Recipes](#ammo-recipes)

```markdown
- [x] Arc capacitor cells
- [x] Plasma charge cells
- [x] Ferromagnetic slugs
- [x] Photonic charge cells
- [x] Compact plasma microcells
- [x] Plasma lance cells
- [x] Plasma projector canisters
- [x] Shock capacitor cells
- [x] Ion charge cells
- [x] Storm capacitor banks
- [x] Disruptor induction cells
- [x] Micro ferromagnetic needles
- [x] Rail sabot penetrators
- [x] Heavy mass-driver slugs
```

# Item Groups

**Head-Category -** [Item Groups](#item-groups)

The mod provides two item-group files:

[Standard sci-fi groups](itemgroups/swa_itemgroups.json)\
[Strict real-world distribution groups](itemgroups/real_itemgroups.json)

```markdown
- [x] Group all sci-fi weapons
- [x] Group all sci-fi ammunition
- [x] Separate plasma, photon, electrical, and magnetic families
- [x] Separate pistols, SMGs/PDWs, rifles, precision guns, and heavy guns
- [x] Separate guns, loose ammunition, and magazines
- [x] Add military, law, research, science, armory, and field-cache hooks
```

# Tileset

**Head-Category -** [Tileset](#tileset)

The mod includes a 32x32 overlay tileset. It is intended for compatible 32x32 tilesets such as Ultica-style sets and does not replace a complete base tileset.

```markdown
- [x] `tileset/scifi_guns_32.png` - 70 gun sprites
- [x] `tileset/scifi_ammo_mags_32.png` - 14 ammunition sprites and 43 magazine sprites
- [x] `tileset/mod_tileset.json` - sprite mappings and compatibility list
```

# Compatibility and Limitations

**Head-Category -** [Compatibility and Limitations](#compatibility-and-limitations)

```markdown
- [x] Target: Cataclysm: Dark Days Ahead H release
- [x] Dependency: `dda`
- [x] Item IDs use the `swa_` prefix
- [x] No UPS dependency
- [x] Passive future-tech armour is defined through JSON
- [x] Future-tech melee weapons are defined through JSON
- [x] No active shields, camouflage, heat system, charging system, or custom item actions
- [x] No furniture, terrain, construction, or vehicles in the current release
- [x] Tiles are an overlay and require a compatible 32x32 tileset
```

# Changelog

**Head-Category -** [Changelog](#changelog)

## 0.9.0-H-release

- Added eight mod-owned future-tech components.
- Added two tool-quality tools, three passive melee weapons, and four passive armour items.
- Added 17 recipes for the new components and equipment.
- Added separate future-tech component, equipment, and field-cache item groups.
- Linked the future-tech field cache into the mod-owned Sci-Fi field-cache group.
- Kept the expansion JSON-only and did not add EOCs because no required custom behaviour was needed.

## 0.8.0-H-release

- Added 26 additional guns.
- Added plasma, photon/laser, electrical, and magnetic weapon families.

## 0.8.1-H-release

- Added ammunition and magazine tiles.
- Added tileset mappings for all ammunition and magazines.
- Reused compatible ammunition and magazine families for the new weapons.

## 0.8.2-H-release

- Updated recipe quality requirements to the H-release object format.

## 0.8.3-H-release

- Clamped recipe difficulties above 10.
- Corrected the plasma projector ammunition reference.
- Replaced the invalid `aluminum` recipe component with `scrap_aluminum`.
- Split gun, ammunition, magazine, item-group, and tileset content into clearer folders.
- Added separated spawn groups and verified the 32x32 mappings.
