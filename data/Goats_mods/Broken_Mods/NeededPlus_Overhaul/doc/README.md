# NeededPlus Overhaul

**Version:** 0.4  
**Game:** Cataclysm: Dark Days Ahead (CDDA)  
**Dependencies:** `dda`  
**Type:** Items, recipes, soft integrations (no mapgen, no hard overrides)

NeededPlus adds **plausible survival processes** the base game is light on—food preservation, dairy, materials—while keeping everything **vanilla-compatible**. It’s fully JSON-only and relies on **safe item-group merges** to blend with vanilla spawns.

---

## Table of contents

1. Design goals & conventions  
2. Modules  
   2.1 Animals & Livestock (NeededPlus)  
   2.2 Canning & Preservation  
   2.3 Cheesemaking & Dairy  
   2.4 Materials & Polymers 2.0  
   2.5 Brewing & Hot Drinks (+ basic distilling)  
   2.6 Beekeeping & Apiary (deployable hive)  
   2.7 Hydroponics (mid-tier, foundations)  
   2.8 Power Distribution & Safety (foundations)  
   2.9 Tailoring Tiers (packs & frames)  
   2.10 Electronics Tiering  
   2.11 Vehicle QoL (light parts)  
   2.12 Bridges & Alt-Inputs (soft additions)  
3. Item spawns & vanilla integration  
4. Quick start guides  
5. Changelog  
6. Install & compatibility  
7. Credits & license

---

## 1) Design goals & conventions

**Design goals**
- **Additive, not replacement.** Vanilla items/recipes remain available.  
- **JSON-only.** No mapgen, no code hooks, no hard overrides.  
- **Vanilla-friendly integration.** Uses soft item-group merges and alt-inputs.  
- **Coherent loops.** Every module stands alone but feeds into others.

**Conventions**
- **Prices:** strings like `"6 USD"` with higher `price_postapoc`.  
- **Colors:** long names only (`light_blue`, `dark_gray`), never `lt_`/`dk_`.  
- **Recipes:** `"activity_level"` is placed **directly under** `"result"`.  
- **Preservation:** canned goods use `jar_glass_sealed` with multi-year `spoils_in`.  
- **Hydration/Nutrition:** modern CDDA style (calories + appropriate spoilage).

---

## 2) Modules

### 2.1 Animals & Livestock (NeededPlus)

**What’s included**
- **Milkable livestock (vanilla workflow):** cows, goats; optionally sheep/water buffalo if present in your build.  
- **Bees (no mapgen):** **Deployable hive** item enabling a honey/propolis loop that connects to canning and medicine.  
- **(Optional) Small stock:** chickens/ducks/rabbits if your build includes them (feeds protein & preservation chains).

**How it works**
- **Milking:** bring a **clean liquid container**, **examine** (`e`) a milkable animal → choose **Milk** → get **raw milk**.  
- Pasteurize via cooking (optional) or use directly in Dairy module recipes.

**Gameplay loop**
- Secure animals (fence, pen), stash feed.  
- **Milk → Curds/Soft/Hard Cheese (rennet & press)**; or **Yogurt/Kefir (cultures)**; or **Butter (+ Whey)**.  
- **Honey/comb** → jams/mead via Brewing & Canning; **Propolis tincture** → antiseptic bridge.

**Spawns & integration**
- Livestock behavior uses **vanilla AI/factions** (compat-safe).  
- **Bees:** deployable hive avoids map edits entirely.

**Notes for modders**
- Mark milkables with the appropriate flags/harvest; keep stats near vanilla for balance.  
- Ensure butchery/hide/organ drops are sane and not exploitable.

---

### 2.2 Canning & Preservation

**What’s included**
- **Tools & supplies:** canning pot (water-bath), **pressure canner**, jar rack, pectin, pickling spice, preservation salt, **canning syrups** (light/medium/heavy).  
- **Water-bath (high-acid):** canned tomatoes, pickled veg mix, fruit jam, fruit in syrup, applesauce.  
- **Pressure (low-acid):** canned beans, meat, fish, potatoes, mushrooms, bone broth, chili, simple vegetable soup.

**How it works**
- Water-bath for high-acid foods; **pressure canning** for low-acid proteins/starches.  
- Products are packed in **`jar_glass_sealed`** with **2–3 years** `spoils_in`.

**Gameplay loop**
- Forage/loot → craft jars/lids (or reuse) → can with the right method → build winter pantry.

**Spawns & integration**
- Item groups:  
  - `NeededPlus_canning_supplies` → **kitchen**/**hardware**  
  - `NeededPlus_canned_goods` → **fridge**

**Notes for modders**
- Recipes rely on **vanilla ingredient categories** (`fruit`, `veggy`, `meat`, `fish`, `broth`, etc.) for broad compatibility.  
- Keep spoilage conservative for balance; multi-year is reserved for properly sealed goods.

---

### 2.3 Cheesemaking & Dairy

**What’s included**
- **Supplies/tools:** `np_rennet`, `np_culture_yogurt`, reusable `np_kefir_grains` (tool), `np_cheesecloth`, `np_mold_cheese_small`, `np_press_small`.  
- **Products:** `np_curds` (**whey** byproduct), `np_soft_cheese`, `np_hard_cheese`, `np_yogurt`, `np_kefir`, `np_butter`, `np_whey`.

**How it works**
- **Curds (rennet)** → drain with cheesecloth; press for soft/hard cheese.  
- **Yogurt** uses culture; **kefir** uses grains (tool, not consumed).  
- **Butter** yields whey as byproduct.

**Gameplay loop**
- Milk livestock → choose a path (cheese / cultured dairy / butter) based on your needs & storage.  
- Pair with **Canning** for jams + cheese boards, or **Brewing** for mead/ales.

**Spawns & integration**
- `NeededPlus_dairy_supplies` → **kitchen**  
- `NeededPlus_dairy_products` → **fridge**

**Notes for modders**
- Shelf lives reflect style (fresh vs pressed vs cultured).  
- Cultures and grains are balanced as tools/consumables to keep a sensible loop.

---

### 2.4 Materials & Polymers 2.0

**What’s included**
- **Composite stack:** epoxy resin/hardener, carbon/fiberglass cloth, **vacuum pump**, bagging/release/peel/breather films, silicone RTV, mold box.  
- **Outputs:** carbon/fiberglass composite panels you can use as craft components.

**How it works**
- Build layup stack → vacuum bag & cure → cut panels → consume in advanced crafts (frames, plates, brackets).

**Gameplay loop**
- Progression path for light, tough parts without touching vehicles/mapgen.

**Spawns & integration**
- `NeededPlus_polymer_supplies` → **chemistry_supplies**  
- `NeededPlus_vacuum_tools` → **hardware**/**electronics**

**Notes for modders**
- Keep power/weight realistic. Use panels as **components** in follow-on crafts (reinforced packs, mounts).

---

### 2.5 Brewing & Hot Drinks (+ basic distilling)

**What’s included**
- **Tea & coffee chain:** loose tea, roasted/ground coffee, kettles/filters/mugs; buffs tuned to CDDA pacing.  
- **Ferment & distill basics:** cider → applejack; sugar mash → moonshine; integrates with NP lab glass bridges.

**How it works**
- Heat/steep for hot drinks morale; ferment + distill with appropriate tools for spirits.

**Gameplay loop**
- Morale/comfort via warm drinks; barterable alcohols; ties into **Canning** (fruit) & **Beekeeping** (honey mead).

**Spawns & integration**
- Uses existing kitchens/chemistry supplies; no mapgen.

**Notes for modders**
- Keep intoxication balanced; preserve vanilla brew clarity.

---

### 2.6 Beekeeping & Apiary (deployable hive)

**What’s included**
- **Deployable hive** (no mapgen), **comb/honey/wax**, **propolis tincture** → **antiseptic bridge**.

**How it works**
- Place hive → harvest comb → process to honey/wax; extract propolis for medicine.

**Gameplay loop**
- Sweetener for jams/teas; wax for crafts; propolis for early medical crafting.

**Spawns & integration**
- Optional wildlife merges for believable honey finds; hive itself is a craftable/deployable.

**Notes for modders**
- Avoid map edits; keep yields modest to prevent easy calorie exploits.

---

### 2.7 Hydroponics (mid-tier, foundations)

**What’s included**
- **Trays**, **nutrient mix**, small **pump/timer**, **light scaffold** items (componentized, no mapgen).

**How it works**
- Treat as craftable infrastructure feeding into vanilla plant growth loops (abstracted, JSON-friendly).

**Gameplay loop**
- Secure, indoor food pipeline in mid-game when scavenging dries up.

**Spawns & integration**
- Light distribution via hardware/electronics where appropriate (optional).

**Notes for modders**
- No custom growth code in this mod; keep it as components used by recipes to avoid maintenance burden.

---

### 2.8 Power Distribution & Safety (foundations)

**What’s included**
- **Inline fuses**, simple **breakers**, **extension cords**, **GFCI outlet** items.

**How it works**
- Use as **requirements or alternatives** in risky/electrical crafts.

**Gameplay loop**
- Encourages safer workshop setups without overhauling power systems.

**Spawns & integration**
- Modest presence in **hardware/electronics** groups.

**Notes for modders**
- These are components/requirements, not systems—keep them optional to remain compatible.

---

### 2.9 Tailoring Tiers (packs & frames)

**What’s included**
- **Makeshift → standard → pro** backpacks/packframes; structured component upgrades and material quality gates.

**How it works**
- Clear improvement path: webbing → framed → reinforced panel inserts (optionally using composites).

**Gameplay loop**
- Long-term carry capacity progression; integrates with **Materials & Polymers**.

**Spawns & integration**
- Crafted progression; can add low-prob spawns to **hardware** for frames, if desired.

**Notes for modders**
- Keep encumbrance reasonable; avoid power creep by gating pro gear behind rare components.

---

### 2.10 Electronics Tiering

**What’s included**
- **Headlamp tiers**, **battery adapters**, small QoL electronics.

**How it works**
- Cheaper early options; pathway to robust pro versions.

**Gameplay loop**
- Early lighting/utility tools that don’t trivialize night play.

**Spawns & integration**
- **electronics**/**hardware** merges for small parts/tools.

**Notes for modders**
- Use standard CDDA tool qualities/charges for consistency.

---

### 2.11 Vehicle QoL (light parts)

**What’s included**
- **Bike panniers**, **jerrycan racks** and similar “lightweight” parts (to avoid heavy vehicle JSON overhauls).

**How it works**
- Add cargo options without touching vehicle spawn maps.

**Gameplay loop**
- Early mobility/carry upgrades; dovetails with Tailoring & Materials.

**Spawns & integration**
- Crafted or lightly merged into **hardware**.

**Notes for modders**
- Keep compatibility with vanilla vehicle IDs; prefer component crafts over direct part overrides.

---

### 2.12 Bridges & Alt-Inputs (soft additions)

**What’s included**
- **Lab/Glass bridges:** distillation/chemistry sets accept NP glass items; glass funnels/goggles via NP glasswork.  
- **Alt-inputs:** conversions so vanilla recipes accept NP goods (e.g., `cheese` ⇐ `np_soft_cheese`/`np_hard_cheese`; `yogurt` ⇐ `np_yogurt`; `butter` ⇐ `np_butter`).

**How it works**
- **Additive** recipes that convert NP items to vanilla counterparts; **no vanilla overrides**.

**Gameplay loop**
- You can live in NP’s ecosystem but still craft vanilla meals/gear seamlessly.

**Spawns & integration**
- No special spawns; bridges ride on existing items.

**Notes for modders**
- Prefer conversions to edits; they’re future-proof and conflict-resistant.

---

## 3) Item spawns & vanilla integration

**NeededPlus item groups** (new content):
- `NeededPlus_canning_supplies`, `NeededPlus_canned_goods`  
- `NeededPlus_dairy_supplies`, `NeededPlus_dairy_products`  
- `NeededPlus_polymer_supplies`, `NeededPlus_vacuum_tools`

**Vanilla merges** (safe, additive):
- `kitchen` ← canning & dairy supplies  
- `fridge`  ← canned goods & dairy products  
- `hardware` ← canning supplies, vacuum tools  
- `electronics` ← vacuum tools  
- `chemistry_supplies` ← polymer supplies

---

## 4) Quick start guides

**Animals & Dairy**  
1) Find milkable animal → bring clean container → **Examine** → **Milk**.  
2) Raw milk → **Curds (rennet)** → **Soft/Hard Cheese**; or **Yogurt/Kefir**; or **Butter (+ Whey)**.

**Canning**  
1) Jars + lids → **Water-bath** (high-acid) or **Pressure** (low-acid).  
2) Store sealed jars (2–3y).

**Composites**  
1) Cut cloth + mix epoxy → bag stack → vacuum → cure → cut panels → consume in advanced crafts.

---

## 5) Changelog (highlights)

- **0.5.5** — Alt-inputs: quick conversions so vanilla meals accept NP cheese/yogurt/butter.  
- **0.5.4** — Cheesemaking & Dairy: rennet/cultures/kefir grains; curds/cheeses/yogurt/kefir/butter; whey; spawns.  
- **0.5.3** — Canning expanded: canning syrups; fruit in syrup/applesauce; fish/potatoes/mushrooms/chili/soup; vanilla categories.  
- **0.5.2** — Canning core: water-bath & pressure canning; sealed jars with multi-year spoilage; spawns; docs.  
- **0.5.0** — Materials & Polymers 2.0: epoxy + vacuum bagging; CF/FG panels; chemistry/electronics/hardware spawns.  
- **0.4.x** — Hydroponics (mid-tier) foundations; power distribution/safety scaffolding; polymer prep.  
- **0.3.x** — Beekeeping mini-loop; deployable hive; honey/propolis; wildlife spawns; antiseptic bridge.  
- **0.2.x** — Brewing & hot drinks; basic fermentation/distillation; nutrition cleanup.  
- **0.1.x** — Tailoring tiers; electronics tiering; lightweight vehicle parts; pricing/color standardization; recipe `activity_level` pass.

---

## 6) Install & compatibility

**Install**
1. Unzip into `mods/`.  
2. Enable **NeededPlus Overhaul** after `dda`.  
3. You can remove subfolders in `crafting/modules/` to disable a module.

**Compatibility**
- **Low-conflict by design.** Everything is additive.  
- Mods that **replace** vanilla item groups (instead of extend) can hide these spawns—load this mod **after** them.

**Safe to add** mid-run. Removing later can orphan items; stash/consume first.

---

## 7) Credits & license

- **Author(s):** You + contributors  
- **Thanks:** CDDA devs & community  
- **License:** (choose: same as CDDA / CC-BY-SA / MIT for JSON)
