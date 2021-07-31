<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  

- [Food Preservation by Irradiation](#food-preservation-by-irradiation)
  - [Whats new to Cataclysm-DDA via this mod:](#whats-new-to-cataclysm-dda-via-this-mod)
  - [Future plans:](#future-plans)
  - [Suggested mods:](#suggested-mods)
  - [Feedback/thoughts](#feedbackthoughts)
    - [Further work consideration:](#further-work-consideration)
    - [Issues](#issues)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Food Preservation by Irradiation
Basically adds in the ability to preserve food via ionizing radiation.

The most likely approach used by a survivor would be x-ray generation.  Such devices are unlikely to be found in the New England area but the right knowledge and parts can enable one to build such a thing in a more portable form.

So after building the device to irradiate food the survivor would
 - Vacuum pack the food item in a plastic bag.
 - Place 1 or several items into the food irradiator and activate it for several minutes.
 - Pull the bagged food which should remain 'fresh' for decades and store it away for tougher times.

## Whats new to Cataclysm-DDA via this mod:
 - A new item 'survival food irradiator' tool which is used in recipies and runs on charges of battery.
 - A new recipe to create the survival food irradiator since it can't be found in the world.
 - A new recipe to create plastic bags.  Due to some unfinished ('todo') code in CDDA 1 plastic chunk = 1 bag but 3 bags = 1 plastic chunk (result_mult doesn't work for items not measured in charges) so for the moment the time to create is significantly reduced.
 - MANY new recipes to transform various food items that you might find into the irradiated counterpart.  No new irradiated foods were added, only recipes to create existing irradiated foods.

## Future plans:
 - When I've sorted out my other code additions, take a look at getting 'result_mult' to work for non-charged items.

## Suggested mods:
 - Rechargeable Batteries which enables small and medium storage batteries to be recharged in the 'battery charger' vehicle part added by Bright Lights mod.

## Feedback/thoughts
The thread is a good place to post feedback about the mod.

### Further work consideration:
 - This last balance pass considered the weight of the goods to be irradiated and spread the cost over batteries and time...
   - Can keep the current spread more or less (I've already heavily squished time in the interest of gameplay) but ceiling to nearby values (ie whole minutes or whole minutes ceiling to nearest divisible by 5).
   - For battery usage, did some squishing here too but not as much but can also ceiling to nearest divisible by 5.

### Issues
 - The balance pass was a bit rough since I don't have good information on exposure or power requirements from real world examples, mostly just rough guesses based loosely on what little info I've found.
 - Also was a bit rough since I haven't stumbled on the units of power in batteries in CDDA.
