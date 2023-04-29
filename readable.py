import sys
import numpy as np

def get_original_ar(map):
	for line in map:
		if line.startswith('ApproachRate'):
			return line.replace('ApproachRate:', '')

def ar_to_ms(ar):
	# Sourced from https://osu.ppy.sh/wiki/en/Beatmap/Approach_rate

	if ar == 5:
		return 1200
	elif ar < 5:
		return 1200 + 600 * (5 - ar) / 5
	else:
		return 1200 - 750 * (ar - 5) / 5

def get_modded_ms(original_ar, ar_setting):
	# Sourced from https://osu.ppy.sh/wiki/en/Beatmap/Approach_rate

	if ar_setting == EZ:
		modded_ar = original_ar * 0.5
		modded_ms = ar_to_ms(modded_ar)
		return modded_ms

	elif ar_setting == HR:
		if original_ar * 1.4 > 10:
			modded_ar = 10
			return ar_to_ms(modded_ar)
		else:
			modded_ar = original_ar * 1.4
			return ar_to_ms(modded_ar)
		
	elif ar_setting == NM:
		return ar_to_ms(original_ar)

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
	timestamps = np.empty(0, dtype=int)
	density_array = np.empty(0, dtype=int)

	for line in map:
		if line.startswith('[HitObjects]'):
			break

	for line in map:
		time = get_raw_timestamp(line)
		if time != 'spinner':
			timestamps = np.append(timestamps, time)

	circle_amount = (np.count_nonzero(timestamps, axis=None))
	for i in range(0, circle_amount):  # The variable "i" represents the particular circle being analyzed.
		circles_on_screen = 1
		if i == (circle_amount - 1):
			density_array = np.append(density_array, circles_on_screen)
		elif timestamps[i + 1] - timestamps[i] > ms:
			density_array = np.append(density_array, circles_on_screen)
			continue
		else:
			for j in range(1, circle_amount):
				if i + j == circle_amount:  # Band-aid solution to prevent next elif from checking for index of circle_amount (index is nonexistent), which breaks program.
					break
				elif timestamps[i + j] - timestamps[i] < ms:
					circles_on_screen = circles_on_screen + 1
				else:
					break
			density_array = np.append(density_array, circles_on_screen)

	return np.reshape(np.append(timestamps, density_array, axis=0), newshape=(2, circle_amount))  # Combines time and density arrays into 2d array.

# working on adjusted density!
def get_orientation(p, coord, coordinates):
	x1, y1, x2, y2, x3, y3 = coord[0], coord[1], coordinates[p, 0], coordinates[p, 1], coordinates[p, 0], coordinates[p, 1]

	slope1 = (y2 - y1) * (x2 - x1)
	slope2 = (y3 - y2) * (x3 - x2)

	if slope1 > slope2:
		return 'clockwise'
	elif slope1 < slope2:
		return 'counterclockwise'
	else:
		if ((x2 <= x1 <= x3) or (x3 <= x1 <= x2)) and ((y2 <= y1 <= y3) or (y3 <= y1 <= y2)):
			return 'collinear-reverse'
		else:
			return 'collinear-straight'

def get_angle(p, coord, coordinates):
	orientation = get_orientation(p, coord, coordinates)

	if orientation == 'collinear-straight':
		angle = 0

	elif orientation == 'collinear-reverse':
		angle = 180

	elif orientation == 'clockwise' or 'counterclockwise':

		a = coord
		b = coordinates[p]
		c = coordinates[p - 1]

		ba = a - b
		bc = c - b

		cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
		angle = np.arccos(cosine_angle)

		if np.isnan(angle):
			angle = 0

		if orientation == 'clockwise':
			angle = -angle

	return angle

def get_distance(point_1, point_2):
    squared_distance = np.sum(np.square(point_1 - point_2))
    return np.sqrt(squared_distance)

def get_distance_diff(p, distance, coordinates):
	return distance - get_distance(coordinates[p], coordinates[p - 1])

def get_stack_obscurity(p, coord, coordinates, ts, timestamps, ms, hitobjects):
	obscurity = 1

	for i in range(np.size(timestamps) - 1, -1, -1):

		if (ts - timestamps[i] < ms) and (np.array_equal(coord, coordinates[i])):
			obscurity = (ts - timestamps[i]) / ms

			if hitobjects[i] == 'slider':
				obscurity = obscurity / 2

	return obscurity

def get_distance_factor(distance):
	if distance != 0:
		return (np.log10(distance / 10)) / 3 + 0.595  # https://www.desmos.com/calculator/q53zdovpss
	else:
		return 0.4

def get_distance_diff_factor(distance_diff):
	if distance_diff > 0:
		return ((np.log10((distance_diff + 170) / 10)) / 3) + 0.595
	else:
		return 1

def get_angle_factor(p, angle, angles):
	if p == 0:
		return 1
	elif np.sign(angle) != np.sign(angles[p]):
		resulting = np.abs(angle) + np.abs(angles[p])
	else:
		resulting = np.abs(angle)

	return ((np.sin(resulting / 458.5)) ** 0.34) + 1  # https://www.desmos.com/calculator/ug1xywioa3

def get_length_factor(hitobject_type, line_stats):
	if hitobject_type == 'circle':
		return 1
	else:
		length = float(line_stats[7])
		return np.cbrt(length / 10000) + 1

def get_stack_factor(stack):
	if stack != 1:
		return ((-1) * np.log10(stack + 2)) + 1.55
	else:
		return 1

def get_adjusted_hitobject(line, p, ms, hitobjects, timestamps, coordinates, angles):
	line_stats = line.split(',')

	hitobject_type = int(line_stats[3])
    
	if hitobject_type == 12:  # Rules out inclusion of spinners in data
		return 'spinner', 'spinner', 'spinner', 'spinner', 'spinner'

	elif bin(hitobject_type).endswith('1'):
		hitobject_type = 'circle'
	else:
		hitobject_type = 'slider'

	ts = int(line_stats[2])
	coord = np.array([(line_stats[0]), (line_stats[1])], dtype=int)

	distance = 0
	distance_diff = 0
	angle = 0
	stack = 0

	if p == -1:
		distance_factor = 1
		distance_diff_factor = 1
		angle_factor = 1
		stack_factor = 1

	elif ts - timestamps[p] < ms:  # Check if the previous hit object is within the time frame to form a line segment
		distance = get_distance(coord, coordinates[p])
		stack = get_stack_obscurity(p, coord, coordinates, ts, timestamps, ms, hitobjects)

		if (ts - timestamps[p - 1] < ms) and (p != 0):  # Check if the 2nd previous hit object is within the time fram to form a triangle with three points
			angle = get_angle(p, coord, coordinates)
			distance_diff = get_distance_diff(p, distance, coordinates)

		distance_factor = get_distance_factor(distance)
		distance_diff_factor = get_distance_diff_factor(distance_diff)
		angle_factor = get_angle_factor(p, angle, angles)
		stack_factor = get_stack_factor(stack)

	length_factor = get_length_factor(hitobject_type, line_stats)

	if not ('distance_factor' in locals()):
		distance_factor = get_distance_factor(distance)
		distance_diff_factor = get_distance_diff_factor(distance_diff)
		angle_factor = get_angle_factor(p, angle, angles)
		stack_factor = get_stack_factor(stack)

	density = distance_factor * distance_diff_factor * angle_factor * length_factor * stack_factor

	if hitobject_type == 'slider':
		slider_stats = line_stats[5]
		slider_stats = slider_stats.split('|')
		last = (slider_stats[-1]).split(':')
		coord = np.array(last, dtype=int)

		# Will later implement system to replace ts with the timestamp in which the slider ends

	return hitobject_type, ts, coord, angle, density

def get_density_per_timestamp(timestamps, densities, ms):
	circle_amount = np.size(timestamps)
	density_per_timestamp = np.empty(0, dtype=float)
	for i in range(0, circle_amount):
		circles_on_screen = 1
		for j in range(1, circle_amount):
			try:
				timestamps[i + j]
			except:
				continue
			if timestamps[i + j] - timestamps[i] < ms:
				circles_on_screen = circles_on_screen + 1
			else:
				break
		sum = 0
		for k in range(i, (i + circles_on_screen)):
			#if k != (circles_on_screen - 1):
			sum = sum + densities[k]

		density_per_timestamp = np.append(density_per_timestamp, sum)
	return density_per_timestamp

def get_adjusted_density(map, path_to_map, ms):
	p = -2  # For indexing purposes.

	hitobjects = np.empty(0, dtype=str)
	timestamps = np.empty(0, dtype=int)
	coordinates = np.empty(0, dtype=int)
	angles = np.empty(0, dtype=float)
	densities = np.empty(0, dtype=float)

	for line in map:
		if line.startswith('[HitObjects]'):
			#  print(line.replace('[HitObjects]', 'e'))
			break

	for line in map:
		p += 1  # For indexing purposes, since line is not an integer

		hitobject_type, ts, coord, angle, density = get_adjusted_hitobject(line, p, ms, hitobjects, timestamps, coordinates, angles)
		if hitobject_type != 'spinner':  # skips every spinner
			
			hitobjects = np.append(hitobjects, hitobject_type)
			timestamps = np.append(timestamps, ts)
			if p > 0:
				coordinates = np.reshape(np.append(coordinates, coord), newshape=(p + 2, 2))  # add reshape with p
			else:
				try:
					coordinates = np.reshape(np.append(coordinates, coord), newshape=(1, 2))
				except:
					coordinates = np.reshape(np.append(coordinates, coord), newshape=(2, 2))


			angles = np.append(angles, angle)
			densities = np.append(densities, density)

		else:
			p -= 1
 
	density_per_timestamp = get_density_per_timestamp(timestamps, densities, ms)

	return np.reshape(np.append(timestamps, density_per_timestamp), newshape=(2, np.size(timestamps)))  # Combines time and density arrays into 2d array.

def start_new_map(path_to_map, ar_setting):
	map = open(path_to_map, 'r', encoding='utf-8')
	ar = float(get_original_ar(map))
	map.seek(0)  # Resets line variable for next instance of 'for line in map'

	ms = get_modded_ms(ar, ar_setting)

	ms = ar_to_ms(ar)
	density_data = (get_adjusted_density(map, path_to_map, ms))
	return density_data