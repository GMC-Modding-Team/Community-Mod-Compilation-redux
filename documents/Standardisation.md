# **Standardisation**

table of contents

* [basic](#basic)
  * [standard json format](#standard json format)

  * [Recipes](#recipes)

* [with code](#with code)

## basic

this is how the json should look inside the compilation

### standard json format

needs abit more info

```json
"id":
"type":
"category":
"name": 
"description": 
"weight":
"volume":
```

### Recipes

``` 
"result":
"type":
"category":
"subcategory":
"difficulty":
"time": 
"components":
"qualities":
"proficiencies":
"skill_used":
"skills_required":
"activity_level":
"autolearn":
```





## with code

with code added

```json
"id": "example_id",
"type": "GENERIC",
"category": "other",
"name": { "str_sp": "bandits charm" }, or "name": { "str": "bandits charm", "str_pl": "bandits charms"  },
"description": "this is an example.",
"weight": "1000 g", or "1 kg"
"volume": "1000 ml", or "1 L",
```

