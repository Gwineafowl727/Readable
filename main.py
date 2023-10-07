import readable
import numpy as np
import sys

np.set_printoptions(threshold=sys.maxsize, suppress=True)

def main():
	map_file = "5150.osu"
	mod = "EZ"
	print("\n")
	print(map_file, mod)
	print(readable.start_new_map(map_file, mod))
	print("\n")

if __name__ == "__main__":
	main()