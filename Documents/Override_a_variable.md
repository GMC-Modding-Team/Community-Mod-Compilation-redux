# Override a variable


Use the `home` key to get to the top.
<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**


- [Links](#links)
  * [Description](#description)
  * [Examples](#examples)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->
---
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
