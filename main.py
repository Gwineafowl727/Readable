import readable
import numpy as np
import sys

np.set_printoptions(threshold=sys.maxsize, suppress=True)

def main():
	map_file = "circles only.osu"
	mod = "EZ"
	print(readable.start_new_map(map_file, mod))

if __name__ == "__main__":
	main()