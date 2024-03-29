# Override a variable

Use the `home` key to get to the top.

**Table of Contents**
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Links](#links)
      - [Head-Category - links](#head-category---links)
  - [Description](#description)
      - [Head-Category  - links](#head-category----links)
      - [Sub-Category - Description](#sub-category---description)
  - [Examples](#examples)
      - [Head-Category - links](#head-category---links-1)
      - [Sub-Category - Examples](#sub-category---examples)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Links

#### Head-Category - [links](#links)


**Sub-Category's:**

[Description](#description)\
[Examples](#examples)

---
## Description #
#### Head-Category  - [links](#links)
#### Sub-Category - [Description](#description)



> If you want to completely override a variable, you shouldn't use extend. If you want to add something to array, use extend. If you want to delete something from array (usually a flag), use delete (same syntax as extend).

---
## Examples
#### Head-Category - [links](#links)
#### Sub-Category - [Examples](#examples)

```JSON
 {
   "type": "mutation",
   "id": "NIGHTVISION",
   "copy-from": "NIGHTVISION",
   "extend": { "category": [ "VAMP" ] }
 }
```

```JSON
"delete": { "effects": [ "NEVER_MISFIRES" ], "flags": [ "IRREPLACEABLE_CONSUMABLE" ] }
```

```JSON
"extend": {
      "map_special": "mx_helicopter",
      "professions": [
        "afs_affluent_executive",
        "afs_wraitheon_executive",
        "afs_vatgrown_bodyguard",
        "afs_bio_operator",
        "afs_holo_fighter"
      ]
    },
```

---
