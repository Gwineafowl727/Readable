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

mod = "NM"
interval = 0.1
low_end = 1
high_end = 6

pair_list = []
low_collection = []
interval_collections = []
high_collection = []

os.chdir(songs_folder_path)

c = 1

for mapset_folder in os.listdir():
    if not mapset_folder.endswith(".txt"):
        mapset_folder_path = f"{songs_folder_path}/{mapset_folder}"
        
        os.chdir(mapset_folder_path)

        if c > 100:  # Limits amount of maps processed for testing purposes
            break

        for file in os.listdir():
            if file.endswith(".osu"):
                
                map_path = f"{mapset_folder_path}/{file}"
                try:
                    rating = start_new_map(map_path, mod)
                    #print(f"{file}\n{rating}\n")
                    
                    if (not np.isnan(rating)) and rating != "not a standard beatmap":
                        pair_list.append((rating, file))
                        c += 1

                except:
                    print("error")
                
        os.chdir(songs_folder_path)

pair_list = sorted(pair_list)

for n, pair in enumerate(pair_list):
    current_index = n

    if pair[0] < low_end:
        low_collection.append(pair[1])
    else:
        break

for i in np.arange(low_end, high_end, interval):

    collection = []
    try:
        within_collection = i <= pair_list[current_index][0] < (i + interval)
    except:
        within_collection = False
        pass

    while within_collection:
        collection.append(pair_list[current_index][1])
        current_index += 1

        try:
            within_collection = i <= pair_list[current_index][0] < (i + interval)
        except:
            within_collection = False
            break
    
    interval_collections.append(collection)

while True:
    try:
        high_collection.append(pair_list[current_index][1])
        current_index += 1
    except:
        break