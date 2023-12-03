import os
import numpy as np
from readable import start_new_map
from osu_db import OsuDb


osu_folder_path = "D:/osu folder/osu!"
collection_db_path = f"{osu_folder_path}/collection.db"
osu_db_path = f"{osu_folder_path}/osu!.db"
songs_folder_path = f"{osu_folder_path}/Songs"

mod = "NM"
interval = 0.1
low_end = 1
high_end = 6

map_info = {}
low_collection = []
interval_collections = []
high_collection = []

os.chdir(songs_folder_path)

test_limit = 1

# Generate giant list of pairs of rating and .osu file name
for mapset_folder in os.listdir():
    if not mapset_folder.endswith(".txt"):
        mapset_folder_path = f"{songs_folder_path}/{mapset_folder}"
        
        os.chdir(mapset_folder_path)

        if test_limit > 1:  # Limits amount of maps processed for testing purposes
            break

        for file in os.listdir():
            if file.endswith(".osu"):
                
                map_path = f"{mapset_folder_path}/{file}"
                try:
                    rating = start_new_map(map_path, mod)
                    
                    if (not np.isnan(rating)) and rating != "not a standard beatmap":

                        map_info[file] = rating
                        test_limit += 1

                except:
                    print("error")
                
        os.chdir(songs_folder_path)

osu_data = OsuDb.from_file(osu_db_path)

pair_list = []

for beatmap in osu_data.beatmaps:
    try:
        rating = map_info[beatmap.osu_file_name.value]
        md5_hash = beatmap.md5_hash.value

        pair_list.append([rating, md5_hash])

    except:
        pass

pair_list.sort(key=lambda x: x[0])
print(pair_list)
