# This file will house the functions for generating collections on specific parameters.

# parameters needed:
# usable collection.db file path
# every single .osu file path in songs folder
# readability rating range selected by user

# 1. run every single map in songs folder through readable.py
# 2. store pairs in some kind of data structure: readability rating, map data that can be converted for collection.db
# 3. sort pairs from least to greatest readability rating
# 4. generate collections. start from the beginning of the data structure and start a new collection
# whenever we reach a new a multiple of the specified increment.