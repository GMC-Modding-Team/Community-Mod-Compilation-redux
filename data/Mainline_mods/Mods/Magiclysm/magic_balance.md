<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

  - [Contents](#contents)
- [Spells](#spells)
    - [Difficulty](#difficulty)
    - [Max Level](#max-level)
    - [Attack Stats](#attack-stats)
    - [Effect](#effect)
    - [Energy Source](#energy-source)
    - [Casting Time](#casting-time)
    - [Energy Cost](#energy-cost)
    - [Fields](#fields)
    - [Damage Type](#damage-type)
    - [Valid targets](#valid-targets)
  - [Tier Examples:](#tier-examples)
    - [Tier 0](#tier-0)
    - [Tier 1](#tier-1)
    - [Tier 2](#tier-2)
    - [Tier 3](#tier-3)
  - [Spellcasting Proficiencies](#spellcasting-proficiencies)
    - [Evocation](#evocation)
    - [Channeling](#channeling)
    - [Conjuration](#conjuration)
    - [Enhancement](#enhancement)
    - [Conveyance](#conveyance)
      - [How The JMATH Works](#how-the-jmath-works)
        - [How JMATH Outputs are Used in Spells](#how-jmath-outputs-are-used-in-spells)
    - [Advice for Using Proficiencies in Spells](#advice-for-using-proficiencies-in-spells)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Contents

- [Spells](#spells)
  - [Difficulty](#difficulty)
  - [Max Level](#max-level)
  - [Attack Stats](#attack-stats)
  - [Energy Source](#energy-source)
  - [Casting Time](#casting-time)
  - [Energy Cost](#energy-cost)
  - [Damage Type](#damage-type)
  - [Valid Targets](#valid-targets)
- [Tier Examples](#tier-examples)
  - [Tier 0](#tier-0)
  - [Tier 1](#tier-1)
  - [Tier 2](#tier-2)
  - [Tier 3](#tier-3)
- [Spellcasting Proficiencies](#spellcasting-proficiencies)
  - [Evocation](#evocation)
  - [Channeling](#channeling)
  - [Conjuration](#conjuration)
  - [Enhancement](#enhancement)
  - [Conveyance](#conveyance)
  - [How The JMATH Works](#how-the-jmath-works)
    - [How JMATH Outputs are Used in Spells](#how-jmath-outputs-are-used-in-spells)
  - [Advice for Using Proficiencies in Spells](#advice-for-using-proficiencies-in-spells)

---

# Spells
Spells are incredibly versatile, and can range wildly depending on the JSON values that are assigned to them. As such, spells can be said to reside in various "tiers" that are based on their stats. The tier of spell is not listed in game, but can be derived based on several factors.

### Difficulty
This is the most obvious way to determine a spell's tier, but not in the way you might expect. A spell with a lower difficulty means the spell is easier to cast, indirectly making it more powerful. Most of the time the difficulty should scale with the tier of the spell, making this rubric a little moot, but it is important to remember that difficulty is a major factor in the spell's failure chance.

### Max Level
Max level both enables the spell difficulty to continue to reduce at higher levels and benefit from continued scaling. A spell with a very small max level (below 10) would have its tier negatively impacted. Max levels above 30 will require significant training in order to reach, and only grows exponentially from there, so be wary of what you expect from a player's spell level.

### Attack Stats
The higher the damage a spell can deal, the higher its tier. This is true for area of effect, duration and range. Most tier 0 and 1 spells don't ever deal more than 150 damage at max level without severe costs.

### Effect
The effect is the main part of the spell, and should be treated as such when balancing it. Entwined with that is the effect_str, which directly affects the effect in various ways. For attack spells, no effect_str wouldn't have an effect on the tier, while adding a "dazed" effect causes the spell's power to skyrocket.

### Energy Source
Energy source is generally related to the class that is assigned to the spell. Stamina would be the type of thing that increases the spell's tier by a significant margin, due to the ease of recovering stamina. Bionic power is relegated to Technomancer, and HP is featured in the Animist class. If spells with spell classes that are not Animist use HP, their tier is automatically higher than if they were to use Mana, which is the normal energy source for spells.

### Casting Time
There are several different ranges of casting times. These include: Fast combat spell (0 - 300 moves) Slow combat spell (300 - 1000 moves) and noncombat spell (longer than 1000 moves) The tier of a spell is quite heavily dependent on its ability to be used quickly in high-pressure situations; so the longer it takes to cast, the more relaxed the tier of the spell can be. A spell would be a very high tier indeed if it took no time to cast; do not do this unless it has severe restrictions.

### Energy Cost
Mana pools can vary, but it is good to balance around the idea that the caster has about 2000 mana to work with. In Magiclysm, spells should be a supplement to your other combat options. This means that at low levels and low tiers, a mage will spend all or nearly all of his mana to deal with low threats: 2-3 zombies or a fat zombie, etc. The tier of a spell will be a good guide to what kind of a threat a mage can conquer at a given level of spell.

### Fields
Fields are currently not very flexible; their duration is fixed, and they do not drift unless they are coded to do so. Most fields would bump the tier level, depending on the field, chance, intensity, etc. Some fields may not bump the tier as they are mostly aesthetic (blood, gore, minor heat, etc)

### Damage Type
Damage type is a key factor in attack spells. Spells that do force damage ignore all armor, and spells that deal cutting, bashing or piercing get blocked by armor. The other damage types get blocked by their associated damage resistance. Until I rewrite the damage function, heat damage also catches the target on fire, cold gets blocked by fire resistance, and the NOBREATHE flag blocks bio damage.

### Valid targets
if your spell is an attack spell and it ignores yourself or allies, it is automatically better than one that does not. If you can target the ground with an attack spell that has aoe, it means you can target out of line of sight.

## Tier Examples:

### Tier 0
Any spell a novice mage would learn as he is learning magic. 
Magic missile: low damage, caps out at 20. however, is force damage so ignores armor, and is target_attack so goes through walls. Has a respectable range and a quick casting time.
Finger firelighter: Useful utility spell, but doesn't really do anything other than allow you to light a fire for the duration of the spell. Lights your square, but has a fairly short duration so does not allow you to read anything with it.
Necrotic Gaze: Does bio damage, which zombies are immune to, and is fairly short range. however, has a fairly high damage at higher levels. Also uses hp to cast, and is fairly cheap.

### Tier 1
A mage is starting to come into his own and use more difficult spells.
Point Flare: somewhat slow for an attack spell, it makes up for its large single-point damage and ability to target through walls. Its casting cost is also fairly low for its damage.
Phase Door: A very useful spell to get you out of immediate danger, but can backfire because it teleports you randomly. Has a fairly high difficulty so its failure chance is high at low levels. Has a quick casting speed so it's able to be used in dire situations, but won't get you very far.
Lightning Bolt: This spell deals damage to all targets in a line, and a good amount of it, too. Its range is fairly short for a ranged spell, but it is quite cheap for a damaging spell. This spell has the rare attribute of having its casting time decrease as its spell level goes up, but has the drawback of being a difficulty of 6 and the LOUD flag. Even though its max damage is quite high, the level required to get there is also quite high.

### Tier 2
These spells are fairly specialized, even in their own class.
Cat's Grace: Along with other similar stat-boosting magus spells, this spell boosts your dexterity stat by 4 for a fairly good duration. It makes up for it by being a slow spell to cast, as you can't really cast it in combat without some preparation. It is also a concentration spell, so focus is a key factor in its failure chance, in addition to being a difficulty 5 spell. The spell can only be cast on the caster, but its max duration is quite high.
Animated Blade: This is a summon spell, and summon spells are generally more powerful than their direct attack cousins by the mere fact that they not only deal damage but absorb damage incoming from monsters. This spell features the animated blade monster, which dishes out a lot of damage; and higher levels in the spell can summon more of them. The spell is very cheap and fast for something that could summon monsters like this, so its difficulty and tier are much higher, and its duration suffers.
Fireball: This is an iconic spell from many Fantasies, but it earns its place at tier 2 by having a large area of effect and a good damage output. Its casting time is just on the edge of being able to be cast easily in combat, and its energy cost is fairly low, even while its damage is quite good in combination with its area of effect. The range of this spell is also quite high, making this spell a favorite of kelvinist mages, even as its difficulty is only 4.

### Tier 3
These spells are even more fantastic or highly specialized.
Translocate Self: This spell has a very niche but powerful spell effect. Even though its casting time precludes it from being cast in combat, its effect allows you to teleport anywhere you created a translocator gate, making it a very useful utility spell. In addition, it is classless, making it even more versatile, useful, and powerful.
Mana Blast: This spell is like fireball, but its damage is even higher, and in addition does force damage and as such ignores armor. That puts this spell squarely in tier 3 alone.

## Spellcasting Proficiencies
Spellcasting proficiencies allow mages to specialize in various kinds of magic, across magic classes, based on what those particular spells do. There are currently five proficieny classes; those being Evocation, Channeling, Conjuration, Enhancement, and Conveyance. 

### Evocation
Evocation covers powerful, short-casting spells that are meant to release large bursts of energy quickly. This covers most offensive spells, such as Magic Missile, Fireball, or Necrotic Gaze. Evocation can also cover non-offensive spells too, so long as they require the caster to pool mana and release it in fast fashion, and their effects aren't covered by one of the other proficiencies. Proficiency in Evocation allows the caster to use mana more efficiently, raising the damage or power of the spell's effect.

### Channeling
Channeling covers spells that require the caster to focus for long periods of time, slowly building or channeling mana over the course of the spell. This includes most rituals, such as Wash the Wounds Clean, Crystalize Mana, or the assorted rune creation spells. The effects of these spells can be most anything. Proficiency in Channeling will reduce the mana cost of the spell and its casting time.

### Conjuration
Conjuration encompasses spells that summon something or someone, usually for a set period of time. Most Golemancy is covered by this, along with the Animist's Summon Undead, Ignus Fattus, or the Druid's Nature's Bow. Conjuration specializes in spells that temporarily summon something, rather than permanently creating something, which would be a bit more suited to Channeling. Proficiency in Conjuration will lower the mana cost of spells and improve the duration times of summoned creatures/objects.

### Enhancement
Enhancement covers spells that improve the target in some way, mentally, physically, or emotionally. While there are many spells in this class, some of them are Cat's Grace, Ogre's Strength, Eagle's Sight, or Feral Form. Note that spells which exclusively heal are not included, as they are fixing something which is damaged, while Enhancement covers spells which improve on the whole. However, if a spell both heals and buffs something, then it should be included in this. Any spells which exclusively debuff or hinder something should also not be included. Proficiency in Enhancement will lower the casting time of spells and improve the duration of enhancement.

### Conveyance
Conveyance encompasses spells which involve translocating, teleporting, or moving the caster/target. Some spells covered are Phase Door, Magus's Mark, Shocking Dash, or Translocate Self. Proficiency in Conveyance will extend the range of the spell (if applicable), or lower the casting time if not, and lower the mana cost of the incantation.

#### How The JMATH Works
The JMATH behind spellcasting proficiencies is fairly simple, this is how it works:

Take for example this function for evocation proficiency bonuses:
```JSON
    "type": "jmath_function",
    "id": "evocation_proficiency_bonus_calculate",
    "num_args": 2,
    "return": "_0 + ((((u_proficiency('prof_magic_evocation_beginner', 'format': 'percent') * 1) / 10) + ((u_proficiency('prof_magic_evocation_apprentice', 'format': 'percent') * 1) / 10) + ((u_proficiency('prof_magic_evocation_master', 'format': 'percent') * 1) / 10)) * _1 )"  
```
What this does is it takes the three associated proficiencies for Evocation (Beginner, Apprentice, and Master) and sees how much you know of that proficiency, on the percent scale of 0% to 100%. It will then take this found value and convert it from a percent to an integer by multiplying it by 1, and this allows the value to be used in `math` calculations. The function then divides the converted integer by 10. This is used for balancing reasons, since initial testing of `math` calculations using a 1 to 1 conversion resulted in spells producing insane damage numbers and costing 0 mana to cast. It repeats this process for all three proficiencies, and then adds them together, giving us a maximum value of 30. This number is used by the game to determine how big of a bonus you get to things like damage and cost reduction, since this maximum value requires that the character master all 3 of these proficiencies in full.

All of the proficiency bonus and negation JMATH functions work the same way, just with different listed proficiencies to calculate off of. One works just like the other, except if it adds or subtracts using the output value.

_0 and _1 will be discussed in [How JMATH Outputs are Used in Spells](#how-jmath-outputs-are-used-in-spells)

##### How JMATH Outputs are Used in Spells
For our next example, let's take a look at the JSON of the classic Kelvinist staple, Point Flare:
```JSON
    "id": "point_flare",
    "type": "SPELL",
    "name": "Point Flare",
    "description": "Generates strong heat at the targeted location, damaging anything susceptible to high temperatures.",
    "valid_targets": [ "hostile" ],
    "flags": [ "CONCENTRATE", "SOMATIC", "LOUD", "NO_PROJECTILE" ],
    "extra_effects": [ { "id": "eoc_evocation_setup", "hit_self": true } ],
    "effect": "attack",
    "shape": "blast",
    "damage_type": "heat",
    "min_damage": { "math": [ "evocation_proficiency_bonus_calculate(16, 0.5)" ] },
    "damage_increment": { "math": [ "evocation_proficiency_bonus_calculate(4.0, 0.0625)" ] },
    "max_damage": { "math": [ "evocation_proficiency_bonus_calculate(80, 0.5)" ] },
    "min_range": 3,
    "range_increment": 0.5,
    "max_range": 11,
    "base_energy_cost": 75,
    "spell_class": "KELVINIST",
    "difficulty": 4,
    "max_level": 16,
    "base_casting_time": 300,
    "energy_source": "MANA"
```

There are a few important numbers out of this that relate to how the previous JMATH is used.

Min and Max Damage:
```JSON
    "min_damage": { "math": [ "evocation_proficiency_bonus_calculate(16, 0.5)" ] },
    "max_damage": { "math": [ "evocation_proficiency_bonus_calculate(80, 0.5)" ] }
```
The first value listed in the `min_damage` and `max_damage` arrays is the base damage of the spell, the _0 in [How The JMATH Works](#how-the-jmath-works). This is what damage the spell would do if the player had no experience at all in Evocation proficiencies, and is what the calculated bonus is added too in the aforementioned example. 0.5 is the _1 that was seen in [How The JMATH Works](#how-the-jmath-works), and this is a scaling modifier. Not all spells do the same damage or scale the same way, so this serves as a way to tune the bonuses of JMATH calculations. In greater detail, this value is what the sum of the three proficiencies is multiplied by at the end of the JMATH calculation to produce the final bonus value, which is added to _0. 

Damage Increments:
```JSON
    "damage_increment": { "math": [ "evocation_proficiency_bonus_calculate(4.0, 0.0625)" ] }
```
Damage increments work off of the same logic as stated above, with 4.0 being the base increase with no proficiency, and 0.0625 being the scaling modifier. In this case, the scaling modifier limits how much bonus damage is added to the spell upon level-up, thus keeping the natural flow of spell progression in check. Without this value, spells would hit their max damage after 4-6 level-ups, giving players no reason to study above that level and breaking magic balance. To find the scaling modifier for damage increments, simply divide the base `damage_increment` with the difference between base `max_damage` and base `min_damage` of the spell in question. Mathematically expressed, it looks like this for Point Flare;
```JSON
    4.0 / (80 - 16)
    4.0 / 64 
      0.0625
``` 
which gives us our result of 0.0625. This already accounts for spell levels and such, so you don't have to worry about that.

This same process can be repeated for all needed calculations in proficiency bonuses and negations. For example, this process applies to `base_energy_cost`, `final_energy_cost`, and `energy_increment` when calculating the proficiency negations on mana costs for Conjuration spells, or `min_duration`, `max_duration`, and `duration_increment` for Enhancement bonusues extending the buff's time.

### Advice for Using Proficiencies in Spells
1. When determining scaling modifiers for proficiency bonuses, remeber to account for the maximum possible bonus (all three proficiencies at 100%, max spell level). If this is not done, then your spell might not scale properly at higher power levels, or become too strong when the player accquires all used proficiencies.
2. Ideally, bonuses should cap around 20% of the base values at maximum proficiency, but this is mainly a rule of thumb. It's up to the discretion of the programmer for how big they want their bonuses to go. So, if something feels to powerful, then reel it back in at bit. If it feels underwhelming, don't be afraid to buff it.
3. When working on spells with multiple effects, such as an `extra_effects` entry, be sure to account for all of the sub-spells and have them use the proper `math` functions. Otherwise, your spell won't scale properly.