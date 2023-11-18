import os
import numpy as np
from readable import start_new_map

# This file will house the functions for generating collections on specific parameters.

# parameters needed:
# usable collection.db file path
# every single .osu file path in songs folder
# readability rating range selected by user

# 1. run every single map in songs folder through readable.py
# 2. store pairs in some kind of data structure: readability rating, map data that can be converted for collection.db
# 3. sort pairs from least to greatest readability rating
# 4. generate collections. start from the beginning of the data structure and start a new collection whenever we reach a new a multiple of the specified increment.

osu_folder_path = "D:/osu folder/osu!"
collection_db_path = f"{osu_folder_path}/collection.db"
songs_folder_path = f"{osu_folder_path}/Songs"

ar = "EZ"

os.chdir(songs_folder_path)

for mapset_folder in os.listdir():
    if not mapset_folder.endswith(".txt"):
        mapset_folder_path = f"{songs_folder_path}/{mapset_folder}"
        
        os.chdir(mapset_folder_path)

        pair_list = []

        for file in os.listdir():
            if file.endswith(".osu"):
                map_path = f"{mapset_folder_path}/{file}"
                try:
                    rating = start_new_map(map_path, ar)
                    print(f"{file}\n{rating}\n")
                    
                    pair_list.append((rating, file))

                except:
                    print("error")

        os.chdir(songs_folder_path)
        pair_list.sort