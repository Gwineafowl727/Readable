import readable
import numpy as np
import sys

np.set_printoptions(threshold=sys.maxsize, suppress=True)

def main():
	map_file = "the big black.osu"
	mod = "NM"
	print(readable.start_new_map(map_file, mod))

if __name__ == "__main__":
	main()