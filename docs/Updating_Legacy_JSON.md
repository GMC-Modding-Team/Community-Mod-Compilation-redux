# Updating Legacy JSON

Use the `home` key to get to the top.

**Table of Contents**
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Introduction](#introduction)
  - [Tools Required](#tools-required)
  - [Regex](#regex)
  - [What is JSON?](#what-is-json)
  - [Terminology in this Document](#terminology-in-this-document)
  - [Python](#python)
- [abstract, ident, and id](#abstract-ident-and-id)
- [Ammo](#ammo)
  - [Ammo Type](#ammo-type)
  - [damage](#damage)
- [Artifacts/relic_data](#artifactsrelic_data)
- [barrel_length](#barrel_length)
- [Bleeding](#bleeding)
- [blob and slime](#blob-and-slime)
- [blueprint](#blueprint)
- [bullet_resist](#bullet_resist)
- [Color](#color)
- [copy-from and looks_like](#copy-from-and-looks_like)
- [Linting](#linting)
- [Materials](#materials)
- [Name](#name)
- [picklock](#picklock)
- [Pocket Data](#pocket-data)
  - [Container Pocket data](#container-pocket-data)
  - [Gun Pocket Data](#gun-pocket-data)
  - [Magazine Pocket Data](#magazine-pocket-data)
  - [CONTAINER](#container)
- [Armor Data](#armor-data)
- [Volume](#volume)
  - [folded_volume](#folded_volume)
- [Weight](#weight)
- [Effect](#effect)
- [Shape](#shape)
- [Construction group](#construction-group)
  - [Group](#group)
- [Activity level](#activity-level)
- [Modinfo](#modinfo)
- [Time](#time)
- [Martial Arts](#martial-arts)
- [Note](#note)
- [item_group](#item_group)
- [vehicle_part](#vehicle_part)
- [Unicode Characters](#unicode-characters)
- [Price](#price)
  - [Melee_damage](#melee_damage)
    - [Resist](#resist)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Introduction

Welcome to Updating Legacy JSON.md. This document aims to guide you through the process of replacing obsolete code with modern JSON.

Before you go any further, I highly recommend you read the [Manual of Style](https://github.com/CleverRaven/Cataclysm-DDA/blob/master/doc/MANUAL_OF_STYLE.md), the [Guide to adding new content to CDDA for first time contributors](https://github.com/CleverRaven/Cataclysm-DDA/wiki/Guide-to-adding-new-content-to-CDDA-for-first-time-contributors), and the [JSON Style Guide](https://github.com/CleverRaven/Cataclysm-DDA/blob/master/doc/JSON_STYLE.md). These three documents provide necessary knowledge to understand CDDA's code.

---
## Tools Required
A lot of obsolete and legacy JSON requires the usage of find-and-replace to bring it up to date. To this end, I recommend that you have a text editor with regex capabilities such as [Sublime Text 3](https://www.sublimetext.com/3), [Notepad++](https://notepad-plus-plus.org/), or [atom](https://atom.io/). I personally find Sublime Text 3 the easiest to work with, but TheGoatGod advocates atom, and many others prefer Notepad++, so find what works best for you.

It can also be useful to have a file searcher on hand if you're editing large quantities of files, or modifying file names. [Grepwin](https://tools.stefankueng.com/grepWin.html) is what I use, and TheGoatGod recommends [Ultrasearch](https://www.jam-software.com/ultrasearch). Again, and I cannot emphasise this enough, use whatever works best for you.
-Goats Comment- I use both tools now, im going to end up with grepwin being my defualt.

You may also see reference to python scripts, in the form `script_name.py` being mentioned in certain entries. See [Python](#Python) for more information on that.

---
## Regex
Regex, short for regular expressions, is a syntax language most commonly used in find-and-replace to find patterns and use complicated replaces. As you'll see later on, even simple regex can massively streamline the process of removing obsolete code. In each section below, I include the specific regex necessary for the task, and how to use it, so don't worry if you don't know what regex is. (For those of you interested in learning more, [Regex Quickstart Cheatsheet](https://www.rexegg.com/regex-quickstart.html) is a great place to start).

---
## What is JSON?
JSON is short for Javascript Object Notation. It is a text format designed to be lightweight and easy for both humans and machines to read and write. JSON is made up of 5 key components: An `array`, an `object`, a `value`, a `number`, and a `string`.

An `array` is started with `[` and ended with `]`. It is composed of `value` separated by `,`. An `object` is started with `{` and ended with `}`. It is, like an array, composed of `value` separated by `,`. A `value` is any other JSON component or `true`, `false`, `null`. A `string` is enclosed in `""` and is a sequence of characters (text). A `number` is simply a number. See [Introducing JSON](https://www.json.org/json-en.html) to learn more.

All of JSON is made up of `key: value` pairs. A `key` is a `string`, while a `value` is a `value`. `array` and `object` are used to format `key: value` pairs, and to provide multiple `value` to a single `key`. Here are some examples of `key: value` pairs used in CDDA code:
```JSON
"flags": [ "SEES", "HEARS", "SMELLS", "POISON", "NO_BREATHE", "REVIVES", "BONES" ]  //A single key contains an array, which then contains multiple values.
"weight": "1000 g"  //A simple key: value pair.
"damage": { "damage_type": "bullet", "amount": 100, "armor_penetration": 4 }  //A single key contains an object, which in turn contains 3 key: value pairs.
"extend": { "effects": [ "FRAG", "EXPLOSIVE_SMALL" ] }  //A key, extend, contains an object value, which in turn contains a key, that contains an array.
"components": [ [ [ "iotvucp", 1 ] ], [ [ "ceramic_plate", 4 ] ] ]  //A key contains an array, which contains an array, which contains an array, which contains 2 value.
```
Note that in the above examples, the single `key` does not contain multiple `value` - the `array` or `object` contains the extra `value`, the `key` `value` is an `array` or `object`.

---
## Terminology in this Document
Throughout this document, I refer to the previous JSON terminology. Any specific `key` will look like `this`, while a key value pair will look like `key: value`. The 5 previously mentioned JSON components will always looke like this: `array`, `value`, `string`, `number`, `object`. Any large block of code (such as the one above), will look like this,
```JSON
key: value,
key: [ value ], //note that these are highlighted in red because plain text inside an array or object must be a string, and thus enclosed in "".
key: { key: value, key: value, key: value }
```

When I provide regex it will always be in the format find entry, empty line, replace entry. If there is no replace entry, **do not replace with nothing**. Here is an example of regex from later in this document:
```regex
"material": "([a-z]+)"

"material": [ "$1" ]
```

---
## Python
Python is a programming language. For the purposes of updating obsolete JSON, it is used to parse and modify text. Don't worry if this makes no sense to you - you don;t actually have to understand what python is to use it. First, install python from [here](https://www.python.org/). Make sure to click 'add python to PATH' in the installer options!

**Windows**
Go to the Tools folder using Windows Explorer.
Type 'cmd' into the address bar.
In cmd, type 'python `<script name>`, replacing <> with the name of the script. Make sure to include '.py'
Respond to the prompt.

**Mac OS**
I don't use filthy macs. You're on your own.

<details>
  <summary> </summary>

  Jk, Access this link [here](https://en.wikibooks.org/wiki/Python_Programming/Creating_Python_Programs)
</details>

**Linux**
If you're using linux, you're probably already familiar with the terminal. Use [this](https://en.wikibooks.org/wiki/Python_Programming/Creating_Python_Programs)

---
# abstract, ident, and id
`abstract` and `id`, are a specific type of `key` that tells the game the unique identifier of the item. Almost every top-level JSON `object` contains an an identifier and a `type`. `type` is an incredibly important `key` that tells the game how to handle the specific `key: value` pairs in the `object`.

`abstract` can only be used on `type: TOOL`, `type: GENERIC`, `type: GUN`, `type: COMESTIBLE`, `type: BOOK`, `type: AMMO`, `type: PET_ARMOR`, `type: vehicle_part`, `type: BIONIC_ITEM`, `type: ARMOR`, `type: TOOLMOD`, `type: ENGINE`, `type: MONSTER`, `type: uncraft`,  `type: overmap_terrain`, and `"type": "recipe",`.

`abstract` creates a pseudo-item that only exists to be copied from and is discarded after JSON loading is complete. If you see it used outside of these fields, replace with `ident` or `id` as appropriate. For debugging purposes, it is preferable to not use `abstract` on types other than `type: overmap_terrain`. It can cause cascading errors that are impossible to find due to lack of item id and presence in the game. See [JSON Inheritance](https://github.com/CleverRaven/Cataclysm-DDA/blob/master/doc/JSON_INHERITANCE.md) for more information on how to use abstract.

`id` can (and perhaps should) be used anywhere `abstract` can be. It is used almost anywhere and doesn't need updating. Check out [JSON Info](https://github.com/CleverRaven/Cataclysm-DDA/blob/master/doc/JSON_INFO.md) for more information on where to use `id`.

`ident` is a third type of `key` that used to be used for the same purpose. It is now deprecated, and should be replaced with `id` wherever possible.

---
# Ammo
The current JSON standards for `type` `"construction_group"` look like this:
```JSON
  "id": "template_ammo",
  "type": "AMMO",
  "name": { "str": "Template_ammo" },
  "description": "Template description.",
  "weight": "10 g",
  "volume": "125 ml",
  "price": 150,
  "price_postapoc": 1000,
  "flags": [ "IRREPLACEABLE_CONSUMABLE" ],
  "material": [ "brass", "powder" ],
  "symbol": "=",
  "color": "yellow",
  "count": 50,
  "stack_size": 50,
  "ammo_type": "Template_type",
  "casing": "Template_casing",
  "range": 14,
  "damage": { "damage_type": "bullet", "amount": 0 },
  "dispersion": 60,
  "recoil": 500,
  "effects": [ "COOKOFF" ]
```

---
## Ammo Type
It is possible to specify the `key: value` pair `ammo: string` under both `type: GUN`, and `type: AMMO`. However, under `type: GUN`, the `key: value` pair should actually be `ammo: [ string ]`.
For reference, here is what it should look like under `type: GUN`:

```JSON
"ammo": [ "300blk" ]
```
And what it should look like under `type: AMMO`:
```JSON
"ammo_type": "300blk"
```

It is practically impossible to replace all at once, due to the similarities between `type: GUN` and `type: AMMO`. However, if you exclude all `type: AMMO` from the search (manually or otherwise), this will work:
```regex
"ammo": "([a -z A -Z]+)",\r

"ammo": "[ "$1" ],
```

---
## damage
The current JSON standards for `key` `"damage"` look like this:
And what it should look like under `type: AMMO`:

```JSON
"damage": { "damage_type": "bullet", "amount": 0 },
```
what it can be
```JSON
"damage": { "damage_type": "bullet", "amount": 0, "armor_penetration": 0 },
```

find:
```REGEX
"damage": ([0-9]+)
or
"damage": ([0-9]+),[\n\r]+    "pierce": ([0-9]+),
```

replace:
```REGEX
"damage": { "damage_type": "bullet", "amount": $1 },
or
"damage": { "damage_type": "bullet", "amount": $1, "armor_penetration": $2 },
```

---
# Artifacts/relic_data
The current JSON standards for `key` `"artifact_data"` **(obsolete)** look like this:

```json
"artifact_data": { "effects_worn": [ "AEP_SUPER_CLAIRVOYANCE" ] }
```

It has been superseded by `key` `"relic_data"` and should look like this now

```json
"relic_data": { "passive_effects": [ { "has": "WORN", "condition": "ALWAYS", "mutations": [ "AEP_SUPER_CLAIRVOYANCE" ] } ] }
```



Example

```json
"artifact_data": { "charge_type": "ARTC_HP", "effects_activated": [ "AEA_ADRENALINE", "AEA_PARALYZE" ] }
```

into

```json
"relic_data": {
      "passive_effects": [
        {
          "has": "WIELD",
          "condition": "ALWAYS",
          "hit_you_effect": [ { "id": "ARTC_HP", "once_in": 3 } ],
          "intermittent_activation": {
            "effects": [ { "frequency": "2 minutes", "spell_effects": [ { "id": "AEA_ADRENALINE" }, { "id": "AEA_PARALYZE" } ] } ]
          }
        }
      ]
    }
```





---
# barrel_length
Very recently, the `barrel_length` `key` for `type: GUN` has been replaced by `barrel_volume`. Fortunately this is a rather easy fix:

```REGEX
"barrel_length":

"barrel_volume":
```

Less recently, at some point, `barrel_length` switched `value` from a `number` to a `string`. The modern JSON looks like this:

```JSON
"barrel_volume": "750 ml"
```
While the obsolete JSON looks like this:
```JSON
"barrel_length": 1
```
The conversion from `number` to `string` is simple - just multiply by 250 and add ml.
```JSON
"barrel_length": 1 = "barrel_length": "250 ml"
"barrel_length": 5 = "barrel_length": "1250 ml"
```

I recommend using `barrellength_volume.py` to convert these values.

---
# Bleeding
I have no idea where to start with this. If you have any information, please feel free to comment.

---
# blob and slime
It turns out that THE BLOB is not the same as the blobs you see around all the time. Check out [blobs are slimes](https://github.com/CleverRaven/Cataclysm-DDA/pull/42287) for more info. Mentions to blob may have to be updated to slime.

---
# blueprint
If you've been directed here from the linting section, it is because you have the parameter "blueprint": "", when it should be "blueprint": [ " " ], - A blueprint must always be enclosed in an array. Since this doesn't actually effect the game in any way (blueprint is exclusively used in the code), adding it just for the purpose of linting should be enough.

---
# bullet_resist
`bullet_resist` is a new mandatory `key: value` pair for `type: material`. If it does not contain `bullet_resist`, it will cause the game to be unable to run. The only way to fix this is to manually add:

```JSON
"bullet_resist": number,
```

---
# Color
Color has gone through updates and there are many variants of it. The currently allowed colours can be found in [Cataclysm-DDA/doc/COLOR.md](https://github.com/CleverRaven/Cataclysm-DDA/blob/master/doc/COLOR.md). Colours other than those allowed should be replaced.

---
# copy-from and looks_like
These are both simple type errors. They should look like:

```JSON
"copy-from": "example_item"
"looks_like": "example_item"
```
But can also be typed:
```JSON
"copy_from": "example_item"
"looks-like": "example_item"
```
Running a basic find and replace for each will clean the code of any errors caused by these.

---
# Linting
Linting is a coding term for formatting to a certain style, and is a very important part of bringing JSON up to date. The simplest way to lint JSON is to paste it into the [JSON formatter](http://dev.narc.ro/cataclysm/format.html), click 'Lint', and then paste the resulting code back into the original file. If it doesn't work, use the debug steps at [JSONLint](https://jsonlint.com/), to check for errors in the code. If it comes up with the error 'Linter currently unavailable', see the [blueprint](#blueprint) section of this document.

It is also possible to use the JSON formatter that comes with CDDA, see the [JSON Style Guide](https://github.com/CleverRaven/Cataclysm-DDA/blob/master/doc/JSON_STYLE.md) for information on how to use it.

---
# Materials
Many items specify a `material: value` pair, which should have an `array` first, like this:

```JSON
"material": [ "plastic" ],
"material": [ "plastic", "steel" ]
```
However, this did not used to be required, so it was specified instead as:
```JSON
"material": "plastic"
```
This is easily fixed with a regex search:
```regex
"material": "([a-z]+)",\r

"material": [ "$1" ],
```

---
# Name
Almost everything that can be seen by characters has a `name: string` `key: value` pair. However, a small subset of these should be specified as:

```JSON
"name": { "str": "pair of socks", "str_pl": "pairs of socks" }
"name": { "str_sp": "irradiated celery" } //use this if the item should not pluralise at all.
```
A good guide as to whether it should be the above code instead of the code below is if it includes a `nam_pl` `key`:
```JSON
"name": "pair of socks",
"name_pl": "pairs of socks"
```

Due to the complexities of replacing the name with regex, I suggest that you use `name.py`, a python script in the Tools folder of this modpack.

---
# picklock
It is very possible that you will see the `use_action` `picklock`. This has been rendered obsolete by the addition of the `quality` `LOCKPICK`. You may see:

```JSON
"use_action": { "type": "picklock", "pick_quality": 5 }
```
Which should be:
```JSON
"qualities": [ [ "LOCKPICK", 5 ] ]
```

This has to be done manually due to the possible presence of other text in the `use_action` and a pre-existing `qualities` key.

---
# Pocket Data
A very notable addition to the 0.E experimental is pocket data. Instead of the previously abstracted storage (of any form), we now have the `key` `pocket_data`. Most notably, `pocket_data` has replaced magazines and containers. These are listed below.  

---
## Container Pocket data
In the past, storage used to be determined by a singular `storage: number` pair. The volume that could be stored, like many things, was the `number` multiplied by `250 ml`.
```JSON
"storage": 0,
"storage": 5
```
Now `pocket_data` looks like this:
```JSON
"pocket_data": [
  {
    "pocket_type": "CONTAINER",
    "rigid": true,
    "max_contains_volume": "4 L",
    "max_contains_weight": "30 kg",
    "moves": 200
  }
]
```
Updating `pocket_data` is fairly time consuming, as each item must be done by manually. The description of the item and similar items are good places to start. If the item has `"storage": 0`, then simply delete `storage`. Following is an example of replacing `storage` with `pocket_data`.

Here's our obsolete JSON (with some fields omitted for brevity).
```JSON
"type": "ARMOR",
"description": "A suit of armor to be used by dirt bikers and motorcyclists.  It has a small pocket intended for you to put your keys and your wallet, if you had some.",
"volume": "1000 ml",
"storage": 2,
...
"flags": [ "VARSIZE" ]
```
From the description, we can see that there's supposed to be one small pocket. As `storage` is 2, the pocket should have a size of 500ml. The flag `VARSIZE` and the relatively small volume of the armor (`1000ml`) indicates that the pocket is non-rigid. Since the pocket is designed to holds keys and a wallet, 2kg is a reasonable max weight.

```json
"type": "ARMOR",
"description": "A suit of armor to be used by dirt bikers and motorcyclists.  It has a small pocket intended for you to put your keys and your wallet, if you had some.",
"volume": "1000 ml",
...
"flags": [ "VARSIZE" ],
"pocket_data": [
  {
    "pocket_type": "CONTAINER",
    "rigid": true,
    "max_contains_volume": "500 ml",
    "max_contains_weight": "2 kg"    
  }        
]
```
And we're done! Don't forget to delete the `storage` key! For more examples, check the JSON of the items in CDDA.

---
## Gun Pocket Data
legacy code just delete These **needs updating**

```JSON
"magazines": [ [ "Example_ammo", [ "Example_magazine1", "Example_magazine2" ] ] ]
"magazine_well": 1
```
new code for guns with magazines
```JSON
"pocket_data": [
  {
    "magazine_well": "250 ml",
    "pocket_type": "MAGAZINE_WELL",
    "holster": true,
    "max_contains_volume": "20 L",
    "max_contains_weight": "20 kg",
    "item_restriction": [ "Example_magazine1", "Example_magazine2" ]
  }
]
```
new code for guns without magazines
```JSON
"pocket_data": [ { "pocket_type": "MAGAZINE", "rigid": true, "ammo_restriction": { "Ammo_example": 100 } } ]
```

---
## Magazine Pocket Data
add these to "type": `Magazine` **needs updating**

```JSON
"pocket_data": [ { "pocket_type": "MAGAZINE", "rigid": true, "ammo_restriction": { "Ammo_example": 30 } } ]
```
or if you want to include more ammo
```JSON
"pocket_data": [ { "pocket_type": "MAGAZINE", "rigid": true, "ammo_restriction": { "Ammo_example_1": 120, "Ammo_example_2": 120 } } ]
```


---
## CONTAINER

The current JSON standards for the `type` `"CONTAINER"` look like this:
`type: CONTAINER` has been obsolete for a while now, and having it in JSON causes error messages. The following should easily remove any problems with `type: CONTAINER`:

```regex
"type": "CONTAINER"

"type": "GENERIC"
```

---
# Armor Data

New code for Armor data

Old code example

```json
"coverage": 10,
"encumbrance": 4,
"cover_melee": 95,
"cover_ranged": 50,
"cover_vitals": 5,
"covers": [ "torso" ]
```

New code example

```json
"armor": [
  {
    "encumbrance": [ 2, 8 ],
    "coverage": 95,
    "cover_melee": 95,
    "cover_ranged": 50,
    "cover_vitals": 5,
    "covers": [ "torso" ]
  }
]
```

---

# Volume

The current JSON standards for the `key` `"volume"` look like this:

```JSON
"volume": "250 ml"
```
With obsolete JSON looking like this:
```JSON
"volume": 1
```
The conversion from `number` to `string` is:
```C++
"volume": 0 = "volume": "1 ml" // This is intentional.
"volume": 1  =  "volume": "250 ml"
"volume": 20  =  "volume": "5000 ml"
"volume": "10000 ml"  =  "volume: 10 L"
```

Unfortunately, updating volume is not as simple as replacing all volume values with their modern version, as volume is also sometimes used to determine the loudness of sounds. However, this is relatively uncommon, so you can often find those specific files and remove them from this search.
```regex
"volume": 1

"volume": "250 ml"
```
And repeat for every individual volume value.

Note: I recommend using `barrellength_volume.py`, a python script found in the Tools folder of this modpack.

## folded_volume
`key` `vehicle_part`:
```JSON
"folded_volume": 5

"folded_volume": "1250 ml"
```

Other:
`"type": "GUNMOD"`
`integral_volume` and `integral_weight` are:
```JSON
"integral_volume": 5,
"integral_weight": 500

"integral_volume": "1250 ml",
"integral_weight": "500 g"
```

---
# Weight
The current JSON standards for `key` `"weight"` look like this:

```JSON
"weight": "100 g"
```
With obsolete JSON looking like this:
```JSON
"weight": 100
```
The conversion from `number` to `string` is:
```C++
"weight": 1  =  "weight": "1 g"
"weight": 20  =  "weight": "20 g"
```

Unfortunately, updating weight is not as simple as replacing all weight values with their modern version, as weight is quite frequently used to determine the probability of a specific piece of terrain spawning in mapgen. Once you have determined that there are no mapgen files in the area you wish to change, you can use this:
```regex
"weight": ([0-9]+),\r

"weight": "$1 g",
```

Note: I once again reccommend using a python script, `weight_update.py` to do this.

---
# Effect
The current JSON standards for `key` `"effect"` look like this: **needs updating**

```JSON
"effect": "attack"
```
With the obsolete json looking like this
```JSON
"effect": "target_attack"
```
with the fix being simple
```JSON
"effect": "target_attack"
into
"effect": "attack"
```

if you want to do this quickly with regex use the following example
```regex
"effect": "([a -zA -Z]+)",

"effect": "attack",
```

---
# Shape
The current JSON standards for `key` `"shape"` look like this: **needs updating**

```JSON
"shape": "blast"
```
all shapes -
```JSON
"line"
"cone"
"blast"
```

---
# Construction group
The current JSON standards for `type` `"construction_group"` look like this:

```Json
"type": "construction_group",
"id": "Example",
"name": "Remove Example"
```

---
## Group
The current JSON standards for `key` `"group"` look like this:

```JSON
"type": "construction",
"id": "constr_example",
"group": "Example",
```

---
# Activity level
The current JSON standards for `key` `"activity_level"` look like this:

```JSON
"activity_level": "EXTRA_EXERCISE",
"activity_level": "ACTIVE_EXERCISE",
"activity_level": "BRISK_EXERCISE",
"activity_level": "MODERATE_EXERCISE",
"activity_level": "LIGHT_EXERCISE",
"activity_level": "NO_EXERCISE",
```

---
# Modinfo
Every mod requires that they have a `modinfo.json` file at the beginning. Several commonly seen issues and their replacements are:
```json
"mod-type": "SUPPLEMENTAL"

"category": "SUPPLEMENTAL"
```
```json
"ident": "mod_id",

"id": "mod_id"
```
```json
"author": "Author1"

"authors": [ "Author1" ],
```

---
# Time
Outdated:
```JSON
"type": "construction",
"time": 100
...
"type": "recipe",
"time": 10000
```

Replacements:

```JSON
"type": "construction",
"time": "100 m"
...
"type": "recipe",
"time": "100 s"
```

---
# Martial Arts
```JSON
"min_melee": 3

"skill_requirements": [ { "name": "melee", "level": 3 }]
```

```JSON
"min_unarmed": 4

"skill_requirements": [ { "name": "unarmed", "level": 4 }]
```
```JSON
"min_unarmed": 3,
"min_melee": 3

"skill_requirements": [ { "name": "unarmed", "level": 3 }, { "name": "melee", "level": 3 } ]
```
If the value of `min_unarmed` or `min_melee` is 0, just delete it.

---
# Note
`key` `note` is deprecated and should be replaced with `//`.
```JSON
"//": "some arbitrary and possibly humorous text that I want whoever reads this JSON to know."

"//": "some arbitrary and possibly humorous text that I want whoever reads this JSON to know."
```

---
# item_group
Item groups should use `prob` instead of `chance`
```JSON
"type": "item_group",
"items": [ { "item": "suit", "chance": 500 }, { "item": "jumpsuit", "chance": 100 }, { "item": "clown_suit", "chance": 1 } ]

"type": "item_group",
"items": [ { "item": "suit", "prob": 500 }, { "item": "jumpsuit", "prob": 100 }, { "item": "clown_suit", "prob": 1 } ]
```

---
# vehicle_part
Vehicle Parts should not have the `key` `range`.
```C++
"type": "vehicle_part",
...
"range": 16 // Delete this.
```

---
# Unicode Characters
As a multinational, multilanguage, game, cdda has no issues with unicode characters. However, the python scripts have issues handling them.

This regex will find all non-ascii (unicode) characters, excluding the ellipsis (…).
```regex
[^\x00-\x7F…]+
```

---
# Price
`key` `price` should have a `value` `string`

```C++
"price": 100,
"price_postapoc": 1000

"price": "100 cent"
"price_postapoc": "10 USD"
"price_postapoc": "10 kUSD"    // Can be cent, USD, or kUSD
```

---

## Melee_damage

```c++
"bashing": 6,
"cutting": 25,

"melee_damage": { "bash": 6, "cut": 25 },
```

### Resist

```c++
"bash_resist": 10,
"cut_resist": 16,
"bullet_resist": 9,
"acid_resist": 6,
"fire_resist": 3,
"elec_resist": 4,

"resist": { "bash": 10, "cut": 16, "acid": 6, "heat": 3, "electric": 4, "bullet": 9 },
```

