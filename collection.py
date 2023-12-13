import os
import numpy as np
from readable import start_new_map
from osuparse import OsuDb
from collectionparse import parse_collections, save_collection
from oce_models import Collections, Collection, CollectionMap


osu_folder_path = "D:/osu folder/osu!"
collection_db_path = f"{osu_folder_path}/collection.db"
osu_db_path = f"{osu_folder_path}/osu!.db"
songs_folder_path = f"{osu_folder_path}/Songs"

mod = "EZ"
interval = 0.5
deci = str(interval)[::-1].find('.')
low_end = 1
high_end = 20

map_info = {}

os.chdir(songs_folder_path)

test_limit = 1

# Generate giant list of pairs of rating and .osu file name
for mapset_folder in os.listdir():
    if not mapset_folder.endswith(".txt"):
        mapset_folder_path = f"{songs_folder_path}/{mapset_folder}"
        
        os.chdir(mapset_folder_path)

        #if test_limit > 1000:  # Limits amount of maps processed for testing purposes
            #break

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

        pair_list.append((rating, md5_hash))

    except:
        pass

pair_list.sort(key=lambda x: x[0])
print(pair_list)

# 1. parse every collection in collection.db and load it into a list of collection objects
# 2. create and append the new collections as collection objects into that same list
# - CollectionMap into list of [CollectionMap] into Collection
# 3. create a Collections object to be used in save_collection

colls = parse_collections(collection_db_path)

low_CollectionMap_list = []
Collection_list = []

for col in colls.collections:
    Collection_list.append(col)

for i, pair in enumerate(pair_list):
    index = i
    if pair[0] < low_end:

        hash = pair[1]
        m = CollectionMap()
        m.hash = hash
        print(m.hash)
        low_CollectionMap_list.append(m)
    
    else:
        break

# collection name str maximum = 25
if low_CollectionMap_list:
    # only include a lower collection if there are any maps that belong
    lc = Collection()
    low_name = f"RR<{low_end}, mod={mod}, v1.1"
    lc.name = low_name
    lc.beatmaps = low_CollectionMap_list
    Collection_list.append(lc)

for i in np.arange(low_end, high_end, interval):

    interval_CollectionMap_list = []
    try:
        within_collection = i <= pair_list[index][0] < (i + interval)
    except:
        within_collection = False
        pass

    while within_collection:
        m = CollectionMap()
        hash = pair_list[index][1]
        m.hash = hash
        interval_CollectionMap_list.append(m)
        index += 1

        try:
            within_collection = i <= pair_list[index][0] < (i + interval)
        except:
            within_collection = False
            break
    
    if not interval_CollectionMap_list:
        # if this interval is empty, don't add to Collection_list
        continue
    ic = Collection()
    interval_name = f"{np.round(i + interval, deci)}<=RR<{np.round(i + interval * 2, deci)}, mod={mod}, v1.1"
    ic.name = interval_name
    ic.beatmaps = interval_CollectionMap_list
    Collection_list.append(ic)

high_CollectionMap_list = []
hc = Collection()
while True:
    try:
        m = CollectionMap()
        hash = pair_list[index][1]
        m.hash = hash
        high_CollectionMap_list.append(m)
        index += 1
    except:
        break

if high_CollectionMap_list:
    high_name = f"{high_end}<=RR, mod={mod}, v1.1"
    hc.name = high_name
    hc.beatmaps = high_CollectionMap_list
    Collection_list.append(hc)

all_collections = Collections()
all_collections.version = colls.version
all_collections.collections = Collection_list

# Delete the currently existing collection.db because
# save_collection keeps writing a BAK file instead

if os.path.exists(collection_db_path):
    os.remove(collection_db_path)

save_collection(all_collections, collection_db_path)