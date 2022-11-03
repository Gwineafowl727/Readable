import linecache
import sys
import numpy as np

def get_original_ar(map):
	for line in map:
		if line.startswith('ApproachRate'):
			return line.replace('ApproachRate:', '')

def ar_to_ms(ar):  # Equations sourced from osu! wiki
	if ar == 5:
		return 1200
	elif ar < 5:
		return 1200 + 600 * (5 - ar) / 5
	else:
		return 1200 - 750 * (ar - 5) / 5

def ms_to_ar(ms):  # Inverse of the function above, essentially
	if ms == 1200:
		return 5
	elif ms > 1200:
		ar = np.round(-((ms - 1800) / 120), decimals=2)
		if (ar).is_integer() == True:
			return int(ar)
		else:
			return ar
	else:
		ar = np.round(-((ms - 1200) / 150) + 5, decimals=2)
		if (ar).is_integer() == True:
			return int(ar)
		else:
			return ar

def get_modded_stats(original_ar, EZ, HR, DT, HT):
	if EZ == 1 and HR == 0 and DT == 0 and HT == 0:  # EZ
		modded_ar = original_ar * 0.5
		modded_ms = ar_to_ms(modded_ar)
		return modded_ar, modded_ms

	elif EZ == 1 and HR == 0 and DT == 1 and HT == 0:  # EZDT
		modded_ar = original_ar / 2
		modded_ms = ar_to_ms(modded_ar) * (2 / 3)
		return ms_to_ar(modded_ms), modded_ms

	elif EZ == 1 and HR == 0 and DT == 0 and HT == 1: # EZHT
		modded_ar = original_ar * 0.5
		modded_ms = ar_to_ms(modded_ar) * (4 / 3)
		return ms_to_ar(modded_ms), modded_ms

	elif EZ == 0 and HR == 1 and DT == 0 and HT == 0:  # HR
		if original_ar * 1.4 > 10:
			modded_ar = 10
			return modded_ar, ar_to_ms(modded_ar)
		else:
			modded_ar = original_ar * 1.
			return modded_ar, ar_to_ms(modded_ar)

	elif EZ == 0 and HR == 1 and DT == 1 and HT == 0:  # HRDT
		if original_ar * 1.4 > 10:
			modded_ar = 10
		else:
			modded_ar = original_ar * 1.4
		modded_ms = ar_to_ms(modded_ar) * (2 / 3)
		return ms_to_ar(modded_ms), modded_ms

	elif EZ == 0 and HR == 1 and DT == 0 and HT == 1:  # HRHT
		if original_ar * 1.4 > 10:
			modded_ar = 10
		else:
			modded_ar = original_ar * 1.4
		modded_ms = ar_to_ms(modded_ar) * (4 / 3)
		return ms_to_ar(modded_ms), modded_ms

	elif EZ == 0 and HR == 0 and DT == 1 and HT == 0:  # DT
		modded_ms = ar_to_ms(original_ar) * (2 / 3)
		return ms_to_ar(modded_ms), modded_ms

	elif EZ == 0 and HR == 0 and DT == 0 and HT == 1:  # HT
		modded_ms = ar_to_ms(original_ar) * (4 / 3)
		return ms_to_ar(modded_ms), modded_ms
	else:
		sys.exit('Conflict with mod selection')  # Put something else during app development

def get_raw_timestamp(line):  # For raw density: each circle and slider will contribute to density equally.
	s = line.split(',')
	hitobject_type = int(s[3])

	if hitobject_type == 12:
		return 'spinner'  # a hit object that is a spinner will not contribute to density.

	else:
		return int(s[2])  # time

def get_raw_density(map, path_to_map, ms):
	c = 0  # The variable "c" acts like a line counter.
	timestamp_array = np.empty(0, dtype=int)
	density_array = np.empty(0, dtype=int)

	for line in map:
		if line.startswith('[HitObjects]'):
			break

	for line in map:
		time = get_raw_timestamp(line)
		if time != 'spinner':
			timestamp_array = np.append(timestamp_array, time)

	circle_amount = (np.count_nonzero(timestamp_array, axis=None))
	for i in range(0, circle_amount):  # The variable "i" represents the particular circle being analyzed.
		circles_on_screen = 1
		if i == (circle_amount - 1):
			density_array = np.append(density_array, circles_on_screen)
		elif timestamp_array[i + 1] - timestamp_array[i] > ms:
			density_array = np.append(density_array, circles_on_screen)
			continue
		else:
			for j in range(1, circle_amount):
				if i + j == circle_amount:  # Prevents next elif from checking for index of circle_amount (index is nonexistent), which breaks program.
					break
				elif timestamp_array[i + j] - timestamp_array[i] < ms:
					circles_on_screen = circles_on_screen + 1
				else:
					break
			density_array = np.append(density_array, circles_on_screen)

	return np.reshape(np.append(timestamp_array, density_array, axis=0), newshape=(2, circle_amount))  # Combines time and density arrays into 2d array.

# working on adjusted density!

def get_distance(point_1, point_2):
    array_1, array_2 = np.array(point_1), np.array(point_2)
    squared_distance = np.sum(np.square(array_1 - array_2))
    distance = np.sqrt(squared_distance)
    return distance

def get_angle_multiplier(coordinate, coordinate_array, d):  # I don't understand most of the math behind this. Basically, it gets the angle in which you have to change direction to aim at the object being calculated.
	if np.array_equal(coordinate, coordinate_array[d-3]) and (not np.array_equal(coordinate_array[d-2], coordinate_array[d-3])):
		turn = 180
	elif np.array_equal(coordinate, coordinate_array[d-2]) or np.array_equal(coordinate_array[d-2], coordinate_array[d-3]):
		return 1
	else:

		a = coordinate
		b = np.array(coordinate_array[d - 2])
		c = np.array(coordinate_array[d - 3])

		ba = a - b
		bc = c - b

		cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
		if np.isnan(cosine_angle):
			angle = 0
		else:
			angle = np.arccos(cosine_angle)  # Angle between vectors

		turn = np.abs(180 - np.degrees(angle))  # Subtracted from 180 to find angle in which you need to turn cursor trajectory.

	angle_multiplier = (np.sin(np.radians(turn / 2))) ** 0.34 + 1  # https://www.desmos.com/calculator/827fzoofho The greater the angle, the closer it gets to a multiplier of 1.
	return angle_multiplier 

def get_adjusted_hitobject(line, coordinate_array, d):
	s = line.split(',')
	hitobject_type = int(s[3])
	coordinate = np.array([int(s[0]), int(s[1])], dtype=int)
	timestamp = int(s[2])

	if hitobject_type == 12:
		return 'spinner', 0, 0  # a hit object that is a spinner will not contribute to density.

	elif bin(hitobject_type).endswith('1'):  # If hit object in question is a circle.

		length_multiplier = 1

	else:  # If hit object in question is a slider. should produce length_multiplier
		raw_length = float(s[7])
		length_multiplier = (raw_length / 10000) ** (1/3) + 1  # https://www.desmos.com/calculator/dl1o5rqfw8

	if d == 1:
		distance_multiplier = 1
	else:

		distance = get_distance(coordinate, coordinate_array[d - 2])
		if distance == 0:
			distance_multiplier = 1
		else:
			distance_multiplier = (np.sin(np.radians((distance * 9) / 8000))) ** 0.2 * (6/5)  # https://www.desmos.com/calculator/smxmzvasad
		
	if d >= 3:    
		angle_multiplier = get_angle_multiplier(coordinate, coordinate_array, d)
	else:
		angle_multiplier = 1

	density = distance_multiplier * angle_multiplier * length_multiplier

	return timestamp, coordinate, density

def get_density_per_timestamp(timestamp_array, density_per_hitobject, ms, circle_amount):
	density_per_timestamp = np.empty(0, dtype=float)
	for i in range(0, circle_amount - 1):
		circles_on_screen = 1
		for j in range(1, circle_amount):
			try:
				timestamp_array[i + j]
			except:
				continue
			if timestamp_array[i + j] - timestamp_array[i] < ms:
				circles_on_screen = circles_on_screen + 1
			else:
				break
		sum = 0
		for k in range(i, (i + circles_on_screen - 1)):
			if k != (circles_on_screen - 1):
				sum = sum + density_per_hitobject[k]

		density_per_timestamp = np.append(density_per_timestamp, sum)
	return density_per_timestamp

def get_adjusted_density(map, path_to_map, ms):
	d = 0  # For indexing purposes.

	timestamp_array = np.empty(0, dtype=int)

	coordinate_array = np.empty(0, dtype=int)

	density_per_hitobject = np.empty(0, dtype=float)

	for line in map:
		if line.startswith('[HitObjects]'):
			#  print(line.replace('[HitObjects]', 'e'))
			break

	for line in map:
		d = d + 1  # For indexing purposes, since line is not an integer

		timestamp, coordinate, density = get_adjusted_hitobject(line, coordinate_array, d)
		if timestamp != 'spinner':  # skips every spinner
			

			timestamp_array = np.append(timestamp_array, timestamp)
			if d != 1:
				coordinate_array = np.reshape(np.append(coordinate_array, coordinate), newshape=(d, 2))
			else:
				coordinate_array = np.append(coordinate_array, coordinate)
			density_per_hitobject = np.append(density_per_hitobject, density)

	circle_amount = d
 
	density_per_timestamp = get_density_per_timestamp(timestamp_array, density_per_hitobject, ms, circle_amount)

	return np.row_stack((timestamp_array, density_per_timestamp))  # Combines time and density arrays into 2d array.

def start_new_map(path_to_map, EZ, HR, DT, HT, adjust):
	map = open(path_to_map, 'r', encoding='utf-8')
	ar = float(get_original_ar(map))
	map.seek(0)  # Resets line variable for next instance of 'for line in map'

	if EZ == 1 or HR == 1 or DT == 1 or HT == 1:
		ar, ms = get_modded_stats(ar, EZ, HR, DT, HT)
	else:
		ms = ar_to_ms(ar)  # Gets the "ms" value, in case there are no mods enabled
	if adjust == 0:  # Make a new function during app development
		density_data = (get_raw_density(map, path_to_map, ms))
	
	else:
		density_data = (get_adjusted_density(map, path_to_map, ms))
	return density_data
  
	# print(density_data)
np.set_printoptions(threshold=sys.maxsize, suppress=True)

print(start_new_map('cycle hit.osu', 0, 0, 0, 0, 1))