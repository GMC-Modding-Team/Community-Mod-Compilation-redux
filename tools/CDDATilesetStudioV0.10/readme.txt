All informations can be found on Cataclysm DDA forum in this thread:
http://smf.cataclysmdda.com/index.php?topic=5686.0

Filter switches
ObjectTree
	:n - use object name instead of object id for filtering
	:e - show only objects without links (without any attached tiles)
LinkTree
	:u - show only tiles without links (without any attached objects)

Planeed features

show Foreground and Background as one image, somewhere
better tooltips
new tile function

Changelog for 0.6

suggested file name when cloning overlay tiles is now similar to names in exported .json
selected tile can now be deleted inside of editor (Tile->Delete or Ctrl+Del), it is possible to delete tile with links, so be careful
links in TileTree are shown as seasonal, if they are (summer foreground) instead of (foreground), for example
when you select link in TileTree, it will also select correct season tab, not just linked object
added filter switches for ObjectTree - :n :e and for TileTree - :u descripnion of filter switches is in Filter switches section

Changelog for 0.7

filtering in ObjectTree made faster (on multicore processers), noticeable difference is with :e switch, rest was fast enough anyway

Changelog for 0.8

new System tiles "explosion_medium" and "explosion_weak"

Changelog for 0.9

fix of importing and exporting bug due to changed paths to tileset files
http://smf.cataclysmdda.com/index.php?topic=11005.0

Changelog for 0.10

support for items with "copy-from" attribute
