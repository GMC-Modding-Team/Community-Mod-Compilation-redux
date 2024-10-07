# Early Survival mod - Primitive Survival

Use the `home` key to get to the top.


# Table of contents

* [To-do](#to-do)
* [Primitive Survival Sources](#primitive-survival-sources)
* [Features](#features)
* [Vanilla-Code](#vanilla-code)
* [Items](#items)
  * [Tools](#tools)
  * [Weapons](#weapons)
  * [Ammo](#ammo)
  * [Generic](#generic)
  * [Containers](#containers)
  * [Resources](#resources)
  * [Materials](#materials)
  * [Clothing](#clothing)
    * [Clothes](#clothes)
    * [Armor](#armor)
  * [Comestibles](#comestibles)
    * [Raw-Fruit](#raw-Fruit)
    * [Drink](#drink)
    * [Food](#food)
    * [Mushrooms](#mushrooms)
    * [Seeds](#seeds)
    * [Medicine](#medicine)
  * [Resources](#resources)
* [Furniture and Terrain](#furniture-and-terrain)
  * [Furniture](#furniture)
  * [Terrain](#terrain)
* [Construction](#construction)
* [Vehicles](#vehicles)
  * [Vehicle-Parts](#vehicle-parts)
* [Recipes](#recipes)
  * [Items](#r-items)
    * [Tools](#r-tools)
    * [Weapons](#r-weapons)
    * [Generic](#r-generic)
    * [Containers](#r-containers)
    * [Materials](#r-materials)
    * [Clothing](#r-clothing)
      * [Clothes](#r-clothes)
      * [Armor](#r-armor)
    * [Comestibles](#r-comestibles)
      * [Drink](#r-drink)
      * [Food](#r-food)
  * [Vehicles](#r-Vehicles)
    * [Vehicle-Parts](#r-vehicle-parts)


# To-do
**Head-Category -** [To-do](#to-do)



*Priority Todos:*
---



```markdown
- [x] Fix `Recipes` to contain all items and `Vehicle-Parts`
- [x] Make `Vanilla` Category
- [x] Make `Resources` Category
- [x] Find out what `Items` have been added already to vanilla game and add to `Vanilla` Category
- [x] Remove all `Items` in vanilla - add extra code to `Vanilla` Category
- [x] Remove all `Materials` in vanilla - add extra code to `Vanilla` Category
- [x] Remove unwanted `Recipes`
- [ ] Add new `Construction` method for building with `Sticks`
- [ ] Add new `Construction` method for building with `Mud`
- [ ] Add new `Construction` method for building with `bamboo`
- [ ] Add more `Items`
- [ ] Add more `Recipes`
- [ ] Add more `Vehicle Parts`
- [ ] Implement a way to collect `Mud`, `Adobe`, and `Leaves`
- [ ] Implement 10 new `professions` and `scenarios` ie, primitive survival easy, normal, hard, other variants that are normal starts like primitive and his dog
- [ ] Add more `bamboo` construction
- [ ] Add more `bamboo` Recipes
- [ ] Add more `bamboo` anything enclosed
```



*For after*
---



```markdown
- [x] Gut `More_tea_leaf` mod
- [x] Gut `Rice` mod
- [x] Gut `Wilderness Overhaul` mod
- [x] Gut `Wild Living` mod
- [x] Gut `Cloth_Rollmat` mod
- [x] Add `Rice` mod to `JSON files`
- [x] Add `Wilderness Overhaul` mod to `JSON files`
- [x] Add `Wild Living` mod to `JSON files`
- [x] Add `Cloth_Rollmat` mod to `JSON files`
- [x] Add `More_tea_leaf` mod to `JSON files`
- [x] Start work on `Wilderness Survival` new `MD` take source over [not sure]
- [x] Start work on `Bush Craft Survival` new `MD` take source over [not sure]
```

# Primitive Survival Sources
**Head-Category -** [Primitive Survival Sources](#primitive-survival-sources)



[Primitive Technology YouTube](https://www.youtube.com/channel/UCAL3JXZSzSm8AlZyD3nQdBA)\
[Primitive Technology Wordpress](https://primitivetechnology.wordpress.com/)\
[Primitive Technology Wordpress Iron Prills](https://primitivetechnology.wordpress.com/2018/08/17/iron-prills/)\
[Primitive Technology Wordpress Wood Ash Cement](https://primitivetechnology.wordpress.com/2018/07/17/wood-ash-cement/)\
[Primitive Technology Wordpress Yam Cultivate and cook](https://primitivetechnology.wordpress.com/2018/06/15/yam-cultivate-and-cook/)\
[Primitive Technology Wordpress Round Hut](https://primitivetechnology.wordpress.com/2018/04/20/round-hut/)\
[Primitive Skills YouTube](https://www.youtube.com/channel/UCs8DNFOxYen3kuj87aWKG9g)\
[Primitive Survival Tool YouTube](https://www.youtube.com/channel/UC6vasuRFx3t3NTISG6iwUeA)\
[Survival Skills Primitive YouTube](https://www.youtube.com/channel/UChUP6B_3zcdFYZnOdMM21og)\
[Tube Unique Wilderness YouTube](https://www.youtube.com/channelUCJjheeAVwFB0S5HlWbBwIfQ)\
[Cambodia Wilderness YouTube](https://www.youtube.com/channel/UC9trIXmdvBIkH2WakrRfK1w)\
[AlfieAesthetics YouTube](https://www.youtube.com/channel/UC2TXg45Dbt2de8auakllW8g)\
[Gone Feral Primitive Skills](https://www.youtube.com/channel/UCaoQ7yYOVjd-8n8nv_r7fXQ)\
[How To Make Roman Concrete](https://www.youtube.com/watch?v=DP0t2MmOMEA)\
[How To Make Ash Cement](https://www.youtube.com/watch?v=DP0t2MmOMEA&ab_channel=PrimitiveTechnology)\
[Primitive Technology: Mud Bricks](https://www.youtube.com/watch?v=D59v74k5flU)\
[Primitive Technology: Fired Clay Bricks](https://www.youtube.com/watch?v=FwRFH7MH5N0&ab_channel=PrimitiveTechnology)\
[Primitive Technology: Brick Firing Kiln](https://www.youtube.com/watch?v=wrTDJbaxhOI&ab_channel=PrimitiveTechnology)\
[Primitive Tool : Make 100 mud brick](https://www.youtube.com/watch?v=Tek3pjCz7BI&ab_channel=PrimitiveSurvivalTool)\
[Making brick the primitive way](https://www.youtube.com/watch?v=V1wS_W9Rt7c)\
[Primitive Building Technology](https://www.youtube.com/channel/UCsNG5AKFeyX_2_GB7ubk9NA)\
[Survival Skills Primitive](https://www.youtube.com/channel/UChUP6B_3zcdFYZnOdMM21og)\
[Sticky rice, Sand Bricks](https://www.youtube.com/watch?v=03fkX98BsHE)\
[Primitive Technology: Furnace and Mud Bricks](https://www.youtube.com/watch?v=v1ebu1hJWcs)\
[Primitive Bricks and Mortar](https://www.youtube.com/watch?v=JfmRKjIJmOQ)\
[Primitive Tool : Make mud brick walls](https://www.youtube.com/watch?v=ou-lOno_2Aw)\
[Brick Oven](https://www.youtube.com/watch?v=Ob9EDRcCaY4)\
[Primitive Tool : Updated grass wall to mud brick wall](https://www.youtube.com/watch?v=hBMOZti_8_U)\
[Primitive Technology: Making Copper Bricks and Making Clay Bricks](https://www.youtube.com/watch?v=0_9rtqvl-iw&ab_channel=SurvivalSkillsPrimitive)\
[Adobe Wall](https://www.youtube.com/watch?v=hzz36cvo88U)\
[Build a Primitive Adobe Rocket Stove (Part 1)](https://www.youtube.com/watch?v=TO3e4NYqr3c)\
[Build a Primitive Adobe Rocket Stove (Part 2)](https://www.youtube.com/watch?v=hcbrIdEEG60)\
[Build a Primitive Adobe Rocket Stove (Part 3)](https://www.youtube.com/watch?v=Htx6d9bz2Yo)\
[Build a Primitive Adobe Rocket Stove (Part 4)](https://www.youtube.com/watch?v=N34CxATbf7Q)



# Features

**Head-Category -** [Features](#features)




```JSON
lots of new items,
```

*How to collect leaves:*
Build menu - build_pile_of_leaves  requires- withered 50
deconstruct pile of leaves to get leaves ATM.



# Vanilla-Code

**Head-Category -** [Vanilla-Code](#vanilla-code)



*Tools:*

```markdown
- [ ] Primitive Knife
- [ ] Primitive Stone Hammer
- [ ] Primitive Hand Axe
- [ ] Primitive Adze
- [ ] Primitive Shovel
- [ ] Mortar And Pestless
- [ ] t_Bellows - Primitive Bellows
- [ ] awl_bone - Primitive Bone Awl
```



*Weapons:*

```markdown
- [ ] bolas - Primitive Bolas
- [ ] slingshot - Primitive Slingshot
```



*Generic:*

```markdown
- [ ] Glue
```



*Materials:*

```markdown
- [ ] Clay
- [ ] Rocks
- [ ] Logs
- [ ] Sticks
- [ ] Long Sticks
- [ ] Grass
```



*Leather clothing:*

```markdown
- [ ] leather_belt - Leather belt
- [ ] dress_shoes -  Leather shoes
```



*Raw-Fruit:*

```markdown
- [ ] Blueberries
- [ ] Raspberries
- [ ] Strawberries
- [ ] Cranberries
- [ ] Grapes
```



*Food:*

```markdown
- [ ] soup_meat - Meat soup
```



*Seeds:*

```markdown
- [ ] seed_barley - Barley Seed - Barley
- [ ] seed_cabbage - Cabbage Seed - Cabbage
- [ ] coffee_pod - Coffee Bean - Coffee
- [ ] seed_grapes - Grape Seed - Grape
- [ ] seed_sugar_beet - Sugar Seed - Cane Sugar
- [ ] seed_tobacco - Tobacco Seed - Tobacco
- [ ] seed_tomato - Tomato Seed - Tomato
- [ ] seed_wheat - Wheat Seed - Wheat
```





# Items

**Head-Category -** [Items](#items)


*All Sub Category's:*\
[Tools](#tools)\
[Weapons](#weapons)\
[Generic](#generic)\
[Seeds](#seeds)\
[Containers](#containers)\
[Materials](#materials)\
[Clothing](#clothing)\
[Comestibles](#comestibles)


## Tools
**Head-Category -** [Items](#items)\
**Sub-Category -** [Tools](#tools)



*Sources:*

[Primitive tools](https://www.survivalsullivan.com/primitive-survival-tools/)\

[Primitive Tools and Weapons](https://secretsofsurvival.com/22-primitive-survival-tools-and-weapons/)



*Items:*

```markdown
- [x] Primitive Oldowan chopping tool
- [x] Primitive Antler
- [x] Primitive Sea Shell Saw
- [x] Primitive Fire_Plough
- [x] Primitive Chisel
- [x] Primitive Stone Tomahawks
```




## Weapons
**Head-Category -** [Items](#items)\
**Sub-Category -** [Weapons](#weapons)



*Sources*

[Primitive Tools and Weapons](https://secretsofsurvival.com/22-primitive-survival-tools-and-weapons/)



*Items:*

```markdown
- [x] Atlatls (A.k.a. Spear Throwers)
- [x] Primitive Blowgun
- [x] Primitive Spears
- [x] Primitive machete
```



## Ammo

**Head-Category -** [Items](#items)\
**Sub-Category -** [Ammo](#ammo)



*Items:*

```markdown
- [x] Blowgun dart
- [x] Blowgun dart crude
```




## Generic
**Head-Category -** [Items](#items)\
**Sub-Category -** [Generic](#generic)



*TODO:*

```markdown
- [ ] Add more `Fertilizer`
```



*Sources:*

[Bonemeal](https://www.agrigem.co.uk/bonemeal-25kg?gclid=CjwKCAjwlbr8BRA0EiwAnt4MTqPYepqJVDBZtOS0pViv8s1zGB-6qnshdM3vnXqOGo8lLMU25pHJ2BoCTBoQAvD_BwE)



*Items:*

```markdown
- [x] Primitive Glue
- [x] Bonemeal Fertilizer
- [x] Primitive Sleeping fur/pelt
- [x] sprouce_bark
- [x] leaves
- [x] Mud
```



## Containers
**Head-Category -** [Items](#items)\
**Sub-Category  -** [Containers](#containers)



*Sources:*

[Sack](https://www.amazon.co.uk/GardenMate-Premium-large-Hessian-Sacks/dp/B00VYM5I9G)



*Items:*

```markdown
- [x] Primitive Backpack
- [x] Primitive Sack
- [x] Primitive Bucket
- [x] Primitive Canteen
```



## Resources

**Head-Category -** [Items](#items)\
**Sub-Category  -** [Resources](#resources)



*Resources:*

```markdown
- [x] Clayston
```



## Materials

**Head-Category -** [Items](#items)\
**Sub-Category  -** [Materials](#materials)



*Items:*

```markdown
- [x] Mud
- [x] Leaves
- [ ] Peat
- [x] Bamboo
- [x] Cloth
```



# Clothing

**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Clothing](#clothing)


*All Sub Category's:*\
[Clothes](#clothes)\
[Armor](#armor)



## Clothes
**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Clothing](#clothing)\
**Sub-Category -** [Clothes](#clothes)



*Cloth Clothing:*

```markdown
- [x] Cloth Cap
- [x] Cloth Shirt
- [x] Cloth Mittens
- [x] Cloth leggings
- [x] Cloth Hood
- [x] Cloth Pants
- [x] Cloth Shoes
- [x] Cloth Jacket
- [x] Cloth Gloves
```



*Leather clothing:*

```markdown
- [x] Leather cap
- [x] Leather shirt
- [x] Leather leggings
- [x] Leather Jacket
- [x] Leather Gloves
```



*Fur clothing:*

```markdown
- [x] Fur Cap
- [x] Fur Shirt
- [x] Fur Mittens
- [x] Fur Leggings
- [x] Fur Hood
- [x] Fur Shoes
- [x] Fur Jacket
- [x] Fur Gloves
- [x] Fur Cloak
```



*Bark:*

```markdown
- [x] bark shoes
- [x] bark cap
```



*Combination clothes:*

```markdown
- [x] Fur-Leather Cap
- [x] Fur-Leather Shirt
- [x] Fur-Leather Leggings
- [x] Fur-Leather Shoes
- [x] Fur-Leather Jacket
- [x] Fur-Leather Mittens
- [x] Fur-Leather Cloak
- [x] Fur-Leather Belt
```



## Armor

**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Clothing](#clothing)\
**Sub-Category -** [Armor](#armor)



*Leather clothing:*

```markdown
- [ ] Leather forearm guards
- [ ] Leather shin guards
- [ ] Leather cuirass
```



*Combination clothes:*

```markdown
- [ ] Fur-Leather forearm guards
- [ ] Fur-Leather shin guards
- [ ] Fur-Leather cuirass
```



# Comestibles

**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Comestibles](#comestibles)

*All Sub Category's:*\
[Raw-Fruit](#raw-Fruit)\
[Drink](#drink)\
[Food](#food)\
[Seeds](#seeds)\
[Medicine](#medicine)



## Raw-Fruit

**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Comestibles](#comestibles)\
**Sub-Category -** [Raw-Fruit](#raw-Fruit)



*Source:*
[Berries Source](https://www.womenfitness.net/cloudberries.htm)



*Raw-Fruit:*

```markdown
- [x] lingonberries
- [x] bilberries
- [x] cloudberries
- [x] crowberries
- [x] black-currants
- [x] gojiberries
- [x] acaiberries
```



## Drink
**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Comestibles](#comestibles)\
**Sub-Category -** [Drink](#drink)



*Sources:*

[berry values](https://www.healthline.com/nutrition/8-healthy-berries#TOC_TITLE_HDR_5)

*Comestibles:*

```markdown
- [x] Blueberry Juice
- [x] Raspberry Juice
- [x] Goji berry Juice
- [x] Strawberry Juice
- [x] Bilberry Juice
- [x] Acai berry Juice
- [x] Grape Juice
- [x] Black-currant juice
- [x] Lingonberries juice
- [x] Cloudberry juice
- [x] Crowberry juice
```


## Food
**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Comestibles](#comestibles)\
**Sub-Category -** [Food](#food)



*Sources:*

[Primitive consumables](https://primitive.fandom.com/wiki/Consumables)



*Items:*

```markdown
- [ ] Cashew Nuts
- [ ] Cashew Milk
- [ ] Ground Cashew Nuts
- [ ] Organic Oil
- [ ] Preserved Jam
- [ ] Flatbread
- [ ] Homemade Soap
- [ ] Meat soup
- [ ] Meat stew
- [ ] Porridge
- [ ] Oven porridge
- [ ] Seed porridge
- [ ] Berry porridge
- [ ] Pea soup
- [ ] Green soup
- [ ] Vegetable soup
- [ ] Mushroom soup
- [ ] Vegetable stew
- [ ] Fillet and Bread
```




## Mushrooms
**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Comestibles](#comestibles)\
**Sub-Category -** [Mushrooms](#mushrooms)



*Sources:*

[Edible Mushrooms](https://en.wikipedia.org/wiki/Edible_mushroom)



*Mushrooms:*

```markdown
- [ ] Black ear mushroom
- [ ] Sand mushroom
- [ ] Noaidi's mushroom
- [ ] Yellowcoat mushroom
- [ ] Browncoat mushroom
- [ ] Bearpaw mushroom
- [ ] Hairy mushroom
- [ ] Redlegger mushroom
- [ ] Yellow fingers mushroom
- [ ] Tellervo's gift mushroom
- [ ] Ukko's mushroom
- [ ] Soft mushroom
- [ ] Ringed mushroom
```


## Seeds
**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Comestibles](#comestibles)\
**Sub-Category -** [Seeds](#seeds)



*Items:*

```markdown
- [x] Lingonberry Seed - Lingonberry
- [x] Bilberry Seed - Bilberry
- [x] Cloudberry Seed - Cloudberry
- [x] Crowberry Seed - Crowberry
- [x] Black-currant Seed - Black-currant
- [x] Goji seed - Goji berries
- [x] Acai seed - Acai berries
- [x] Breadfruit Seed - Breadfruit
- [x] Cashew Seed - Cashew Nut
- [x] Rice Seed - Rice
- [x] Turnip seed - Turnip
- [x] Swede seed - Swede
- [x] Pea seed - Pea shoot
- [x] Broad Bean seed - Broad Bean
- [x] Rye seed - Rye
- [x] Hemp seed - Hemp
```



## Medicine
**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Comestibles](#comestibles)\
**Sub-Category -** [Medicine](#medicine)





# Resources

**Head-Category -** [Items](#items)\
**Sub-Head-Category -** [Resources](#resources)



*Wood:*

```markdown
- [ ] Firewood
```



# Furniture and Terrain

**Head-Category -** [Furniture and Terrain](#furniture-and-terrain)


*All Sub Category's:*\
[Furniture](#furniture)\
[Terrain](#terrain)



## Furniture

**Head-Category -** [Furniture and Terrain](#furniture-and-terrain)\
**Sub-Category -** [Furniture](#furniture)



*Construction:*

```markdown
- [ ] Apiary
- [ ] Bakers Oven
- [ ] Cauldron
- [ ] Fireplace
- [ ] Firewood Holder
- [ ] Fruit Press
- [ ] Grill
- [ ] Hand mill
- [ ] Spinning Mule
- [ ] Storage Barrel
- [ ] Tanning Rack
- [ ] Weapon Rack
```



## Terrain

**Head-Category -** [Furniture and Terrain](#furniture-and-terrain)\
**Sub-category -** [Terrain](#terrain)



*Mud Terrain:*

```markdown
- [ ] Mud Door-frame
- [ ] Mud Door
- [ ] Mud Floor
- [ ] Mud Window-frame
- [ ] Mud Window
- [ ] Mud Wall
- [ ] Mud Roof
```



*Stick Terrain:*

```markdown
- [ ] Stick Door-frame
- [ ] Stick Door
- [ ] Stick Floor
- [ ] Stick Window-frame
- [ ] Stick Window
- [ ] Stick Wall
- [ ] Stick Roof
```



*Terrain flora:*

```markdown
- [x] Cranberry Shrub
- [x] Lingonberry Shrub
- [x] Bilberry Shrub
- [x] Cloudberry Shrub
- [x] Crowberry Shrub
- [x] Black-currant Shrub
- [x] Goji Shrub
- [x] Bilberries Shrub
- [x] Acai Shrub
- [x] Birch Tree
- [x] Spruce Tree
- [x] Breadfruit Tree
- [x] Cashew Tree
- [x] Rubber Tree
- [x] Rice Shrub
- [x] Turnip Shrub
- [x] Swede Shrub
- [x] Pea Shrub
- [x] Broad Bean Shrub
- [x] Rye Shrub
- [x] Hemp Shrub
```



*Mushrooms:* **needs proper naming to be included**

```Markdown
https://en.wikipedia.org/wiki/Edible_mushroom
```

```markdown
- [ ] Black ear mushroom
- [ ] Sand mushroom
- [ ] Noaidi's mushroom
- [ ] Yellowcoat mushroom
- [ ] Browncoat mushroom
- [ ] Bearpaw mushroom
- [ ] Hairy mushroom
- [ ] Redlegger mushroom
- [ ] Yellow fingers mushroom
- [ ] Tellervo's gift mushroom
- [ ] Ukko's mushroom
- [ ] Soft mushroom
- [ ] Ringed mushroom
```



# Construction

**Head-Category -** [Construction](#construction)



*Sources:*

```markdown
https://primitivetechnology.wordpress.com/2018/04/20/round-hut/
```



*Tools:*

```markdown
- [ ] Apiary
- [ ] Bakers Oven
- [ ] Cauldron
- [ ] Fireplace
- [ ] Firewood Holder
- [ ] Fruit Press
- [ ] Grill
- [ ] Hand mill
- [ ] Spinning Mule
- [ ] Storage Barrel
- [ ] Tanning Rack
- [ ] Weapon Rack
```



*Mud Terrain:*

```markdown
- [ ] Mud Door-frame
- [ ] Mud Door
- [ ] Mud Floor
- [ ] Mud Window-frame
- [ ] Mud Window
- [ ] Mud Wall
- [ ] Half-built Mud Wall
- [ ] Mud Roof
```



*Stick Terrain:*

```markdown
- [ ] Stick Door-frame
- [ ] Stick Door
- [ ] Stick Floor
- [ ] Stick Window-frame
- [ ] Stick Window
- [ ] Stick Wall
- [ ] Stick Roof
```



# Vehicles

**Head-Category -** [Vehicles](#vehicles)


*All Sub Category's:*\
[Vehicle-Parts](#vehicle-parts)



*Vehicles:*

```markdown
- [x] Raft - 6 Strapped wood, Tying equipment, Mast, Steering stick attached to steering wood
- [ ] Large Raft - 16 Strapped wood, Tying equipment, Large mast, Steering stick attached to steering wood
- [ ] Materials Cart - Sticks, Tying equipment
```



## Vehicle-Parts

**Head-Category -** [Vehicles](#vehicles)\
**Sub-Category -** [Vehicle-Parts](#vehicle-parts)



*Items:*

```markdown
- [ ] Strapped wood
- [ ] Mast
- [ ] Large Mast
- [ ] Steering stick attached to steering wood
```



# Recipes

**Head-Category -** [Recipes](#recipes)


*All Sub Category's:*\
[Items](#r-items)\
[Vehicles](#r-Vehicles)



## R-Items

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)

*All Sub Category's:*\
[Tools](#r-tools)\
[Weapons](#r-weapons)\
[Generic](#r-generic)\
[Containers](#r-containers)\
[Materials](#r-materials)\
[Clothing](#r-clothing)\
[Comestibles](#r-comestibles)



## R-Tools

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category -** [Tools](#r-tools)



*TODO:*

```markdown
- [x] add `Tools` from `Items` Category
- [ ] Sort `Unfinished-Items` into `Finished-Items`
```



*Items:*

```markdown
- [ ] Primitive Grain Grinders
- [ ] Primitive Mortar And Pestless
- [ ] Primitive Oldowan chopping tool
- [ ] Primitive Antler
- [ ] Primitive Sea Shell Saw
- [ ] Primitive Chisel
```



*Finished-items*

```markdown
- [ ] Birch-bark box  - birch-bark, knife
- [ ] Birch-bark basket - birch-bark, knife
- [ ] Birch-bark rope - birch-bark, knife, water - (tying equipment)
- [ ] Birch withe - Birch-wood, knife - (tying equipment)
- [ ] Spruce withe - Spruce-wood, knife - (tying equipment)
- [ ] Leather Rope - knife, water, leather - (tying equipment)
- [ ] cordage - cloth, knife - (tying equipment)
- [ ] Wooden stake - wood
```



## R-Weapons

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category -** [Weapons](#r-weapons)



*TODO:*

```markdown
- [ ] Sort `Unfinished-Items` into `Finished-Items`
```



*Unfinished-Items:*

```markdown
- [ ] Primitive Spears
- [ ] Primitive Stone Tomahawks
- [ ] Primitive Hoko Knives
- [ ] Primitive Blowgun
- [ ] Primitive Dagger
- [ ] Primitive Sword
- [ ] Primitive Staff
- [x] Atlatls (A.k.a. Spear Throwers) - take from code already made
```



## R-Generic

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category -** [Generic](#r-generic)



*TODO:*

```markdown
- [x] add `Generic` from `Items` Category
- [ ] Sort `Unfinished-Items` into `Finished-Items`
```



*Sources:*
[Primitive glue](https://www.outdoorrevival.com/instant-articles/making-glue-stick-using-primitive-methods.html)
[Bonemeal Fertilizer](https://balconygardenweb.com/how-to-make-bone-meal-fertilizer-at-home/)



*Unfinished-Items:*

```markdown
- [ ] Primitive Glue
- [ ] Bonemeal Fertilizer
- [ ] Primitive Sleeping fur/pelt
- [ ] sprouce_bark
- [ ] leaves
- [ ] Mud
```



## R-Containers

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category -** [Containers](#r-containers)



*TODO:*

```markdown
- [ ] Sort `Unfinished-Containers` into `Containers`
```



*Containers:*

```markdown
- [ ] Primitive Backpack - Primitive Sack, Cord - bone awl
- [ ] Primitive Sack - Cord - Bone awl
- [ ] Primitive Bucket - Wood, Cord - Cutting tool
- [ ] Primitive Canteen - Wood, Chisel - Cutting tool
```



*Unfinished-Containers:*

```markdown
- [ ] Primitive Canteen
```



## R-Materials

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category -** [Materials](#r-materials)



*TODO:*

```markdown
- [x] add `Materials` from `Items` Category
```



*Items:*

```markdown
- [ ] Claystone
- [ ] Mud
- [ ] Leaves
- [ ] Peat
```



# R-Clothing

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category-Header -** [Clothing](#r-clothing)

*All Sub Category's:*\
[Clothes](#r-clothes)\
[Armor](#r-armor)



## R-Clothes

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category-Header -** [Clothing](#r-clothing)\
**Sub-Category -** [Clothes](#r-clothes)



*Cloth Clothing:*

```markdown
- [ ] Cloth Cap
- [ ] Cloth Shirt
- [ ] Cloth Mittens
- [ ] Cloth leggings
- [ ] Cloth Hood
- [ ] Cloth Pants
- [ ] Cloth Shoes
- [ ] Cloth Jacket
- [ ] Cloth Gloves
```



*Leather clothing:*

```markdown
- [ ] Leather cap
- [ ] Leather shirt
- [ ] Leather leggings
- [ ] Leather Jacket
- [ ] Leather Gloves
```



*Fur clothing:*

```markdown
- [ ] Fur Cap
- [ ] Fur Shirt
- [ ] Fur Mittens
- [ ] Fur Leggings
- [ ] Fur Hood
- [ ] Fur Shoes
- [ ] Fur Cloak
- [ ] Fur Jacket
- [ ] Fur Gloves
```



*Birch-bark:*

```markdown
- [ ] Birch-bark shoes
- [ ] Birch-bark cap
```



*Source-bark:*

```markdown
- [ ] Source-bark shoes
- [ ] Source-bark cap
```



*Combination clothes:*

```markdown
- [ ] Fur-Leather Belt
- [ ] Fur-Leather Cap
- [ ] Fur-Leather Shirt
- [ ] Fur-Leather Leggings
- [ ] Fur-Leather Shoes
- [ ] Fur-Leather Jacket
- [ ] Fur-Leather Cloak
- [ ] Fur-Leather Mittens
```



## R-Armor

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category-Header -** [Clothing](#r-clothing)\
**Sub-Category -** [Armor](#r-armor)



*TODO:*

```markdown
- [ ] add `Armor` from `Items` Category
```



*Leather clothing:*

```markdown
- [ ] Leather forearm guards
- [ ] Leather shin guards
- [ ] Leather cuirass
```



*Combination clothes:*

```markdown
- [ ] Fur-Leather forearm guards
- [ ] Fur-Leather shin guards
- [ ] Fur-Leather cuirass
```



# R-Comestibles

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category-Header -** [Comestibles](#r-comestibles)


*All Sub Category's:*\
[Drink](#r-drink)\
[Food](#r-food)\
[Seeds](#r-seeds)



## R-Drink

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category-Header -** [Comestibles](#r-comestibles)\
**Sub-Category -** [Drink](#r-drink)



*TODO:*

```markdown
- [x] add `Drink` from `Items` Category
- [x] `Juices` Recipes
- [x] `Juice` Recipes
- [ ] Primitive `Tea` Recipes
- [ ] Primitive `Coffee` Recipes
```



*Unfinished-Comestibles:*

```markdown
- [x] Blueberry Juice
- [x] Raspberry Juice
- [x] Goji berry Juice
- [x] Strawberry Juice
- [x] Bilberry Juice
- [x] Acai berry Juice
- [x] Grape Juice
```



## R-Food

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category-Header -** [Comestibles](#r-comestibles)\
**Sub-Category -** [Food](#r-food)



*TODO:*

```markdown
- [x] add `Food` from `Items` Category
- [ ] add process to `Unfinished Food`
- [ ] add `Unfinished food` to `Finished Food`
- [ ] add more `Breads`
```



*Finished Food:*

```markdown
- [ ] Homemade Soap - water, vegetables, seasoning - knife - boil
- [ ] Meat soup - raw meat, water, vegetables, seasoning - knife - boil
- [ ] Meat stew - raw meat, water, vegetables, seasoning - knife - bake
- [ ] Porridge - flour, Water - boil
- [ ] Oven porridge - flour, water - Bake
- [ ] Seed porridge - flour, seed, water - boil
- [ ] Berry porridge - flour, berry, water - boil
- [ ] Fish Fillet - raw fish, water, vegetables, seasoning - knife - boil
- [ ] Pea soup - peas, water, raw meat, seasoning - boil
- [ ] Green soup - herbs, water, flour, seasoning - boil
- [ ] Vegetable soup - vegetables, water, seasoning - boil
- [ ] Mushroom soup - mushrooms, water, flour, seasoning - boil
- [x] Vegetable and meat stew - vegetables, water, mushrooms, seasoning - bake
```



*unfinished food:*

```markdown
- [x] Cashew Nuts
- [ ] Cashew Milk
- [ ] Ground Cashew
- [ ] Organic Oil
- [ ] Preserved Jam
- [ ] Flatbread
```



## R-Seeds

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Items](#r-items)\
**Sub-Category-Header -** [Comestibles](#r-comestibles)\
**Sub-Category -** [Seeds](#r-seeds)



seeds:

```markdown
- [x] Lingonberry Seed - Lingonberry
- [x] Bilberry Seed - Bilberry
- [x] Cloudberry Seed - Cloudberry
- [x] Crowberry Seed - Crowberry
- [x] Black-currant Seed - Black-currant
- [x] Rice Seed - Rice
- [x] Turnip seed - Turnip
- [x] Swede seed - Swede
- [x] Pea seed - Pea shoot
- [x] Broad Bean seed - Broad Bean
- [x] Rye seed - Rye
- [x] Goji seed - Goji berries
- [x] Bilberries seed - Bilberries
- [x] Acai seed - Acai berries
```



# R-Vehicles
**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Vehicles](#r-Vehicles)


*All Sub Category's:*\
[Vehicle-Parts](#r-vehicle-parts)



## R-Vehicle-Parts

**Head-Category -** [Recipes](#recipes)\
**Sub-Head-Category -** [Vehicles](#r-Vehicles)\
**Sub-Category -** [Vehicle-Parts](#r-vehicle-parts)



*TODO:*

```markdown
- [x] add `Vehicle-Parts` from `Vehicles` Category
- [x] add `Unfinished-Items` to `Items`
```



*Items:*

```markdown
- [ ] Strapped wood - cordage or leather rope or rope or fibre rope, 2 logs. - Saw, axe
- [ ] Mast - 7 sticks, Sheet
- [ ] Large Mast - 1 log, 4 Sheets
- [ ] Steering stick attached to steering wood - stick, log - cutting tool
```
