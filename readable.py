import numpy as np

class circle:
	def __init__(self, timestamp, x, y, euclidean_distance, angle):
		self.timestamp = timestamp
		self.x = x
		self.y = y
		self.euclidean_distance = euclidean_distance
		self.angle = angle

class slider:
	def __init__(self, timestamp_start, timestamp_end, x_start, y_start, x_end, y_end, curve_array, movement, euclidean_distance, angle, reverse):
		self.timestamp_start = timestamp_start
		self.timestamp_end = timestamp_end
		self.x_start = x_start
		self.y_start = y_start
		self.x_end = x_end
		self.y_end = y_end
		self.curve_array = curve_array
		self.movement = movement
		self.euclidean_distance = euclidean_distance
		self.angle = angle
		self.reverse = reverse

class curvePoint:
	def __init__(self, x, y):
		pass
	

def get_original_ar(map):
	for line in map:
		if line.startswith("ApproachRate"):
			return line.replace("ApproachRate:", "")

def ar_to_ms(ar):
	# Equations sourced from osu! wiki
	if ar == 5:
		return 1200
	elif ar < 5:
		return 1200 + 600 * (5 - ar) / 5
	else:
		return 1200 - 750 * (ar - 5) / 5

def ms_to_ar(ms):
	# Inverse of the function above, essentially
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

def get_distance_factor(x1, y1, x2, y2):
	# "1" indicates current hitobject, "2" indicates previous.
	euclidean_distance = np.sqrt((x1 - x2)**2 - (y1 - y2)**2)
	return ((np.log(euclidean_distance / 10) / 3) + 0.595), euclidean_distance

def get_delta_distance_factor(d1, d2):
	# "1" indicates current hitobject, "2" indicates previous.
	difference = d1 - d2
	if difference > 0:
		return ((np.log(difference + 170) / 10 ) / 3) + 0.595
	else:
		# for if the difference is negative, i.e. a decelerating stream
		return ((np.log(difference + 340) / 10 ) / 4) + 0.595
	
def get_angle_factor(x1, y1, x2, y2, x3, y3, hitobject_list):

	# Trying to understand this again is giving me cancer so please just trust that it works !!
	slope1 = (y2 - y1) * (x2 - x1)
	slope2 = (y3 - y2) * (x3 - x2)

	if slope1 > slope2:
		orientation = 'clockwise'
	elif slope1 < slope2:
		orientation = 'counterclockwise'
	else:
		if ((x2 <= x1 <= x3) or (x3 <= x1 <= x2)) and ((y2 <= y1 <= y3) or (y3 <= y1 <= y2)):
			oritentation = 'collinear-reverse'
		else:
			orientation = 'collinear-straight'

	if orientation == 'collinear-straight':
		angle = 0

	elif orientation == 'collinear-reverse':
		angle = 180

	else:
		# Angle between two vectors
		a = np.array([x1, y1])
		b = np.array([x2, y2])
		c = np.array([x3, y3])

		ba = a - b
		bc = c - b

		cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
		angle = np.arccos(cosine_angle)

		if np.isnan(angle):
			angle = 0

		if orientation == 'clockwise':
			angle = -angle

	if np.sign(angle) != np.sign(hitobject_list[-1].angle):
		resulting = np.abs(angle) + np.abs(hitobject_list[-1].angle)
	else:
		resulting = np.abs(angle)

def get_stack_factor(stack_ms, type_current, type_previous):

	if type_current == circle:

		if type_previous == "circle" or "sliderstart":
			return np.log10(stack_ms * 5 + 2) + 0.7
		else:
			return np.log10(stack_ms + 2) + 0.7

	if type_current == slider:
		pass


def get_object_range(hitobject_list, object_timestamp, map_ms):

	if len(hitobject_list) == 0:
		return 0
	
	in_view = 0
	for i in range(len(hitobject_list) - 1, -1, -1):

		if type(hitobject_list[i]) == circle:
			if object_timestamp - hitobject_list[i].timestamp >= map_ms:
				in_view += 1

		else:  # Is basically the same as the if statement above, but accounts for slider attribute name
			if object_timestamp - hitobject_list[i].timestamp_end >= map_ms:
				in_view += 1

	return in_view

def get_raw_circle(line_stats, hitobject_list, map_ms):
	# Return information about the circle and its raw density

	# x, y, millisecond timestamp
	x_coord = line_stats[0]
	y_coord = line_stats[1]
	object_timestamp = line_stats[2]

	# Last two attributes are euclidean distance and angle. 0 is a placeholder that will be replaced if necessary.
	hitobject = circle(x_coord, y_coord, object_timestamp, 0, 0)
	object_range = get_object_range(hitobject_list, object_timestamp, map_ms)

	# For if there are no other hitobjects in view before current hitobject
	if object_range == 0:
		raw_density = 1  # A lonely circle on the screen should be density 1. right?
		return hitobject, raw_density

	for i in range(object_range):

		x1, y1 = hitobject.x, hitobject.y

		if i == 1:
			if type(hitobject_list[-1]) == circle:
				distance_factor, euclidean_distance = get_distance_factor(x1, y1, hitobject_list[-1].x, hitobject_list[-1].y)

			elif not hitobject_list[-1].movement:
				# last hitobject is a slider and if slider requires no movement, distance_factor will treat the slider start position as a hit circle, using its start position.
				distance_factor, euclidean_distance = get_distance_factor(x1, y1, hitobject_list[-1].x_start, hitobject_list[-1].y_start)

			else:
				# If last hitobject is a slider that requires movement, distance_factor will be using the end of the slider.
				distance_factor, euclidean_distance = get_distance_factor(x1, y1, hitobject_list[-1].x_end, hitobject_list[-1].y_end)
				
			setattr(hitobject, "euclidean_distance", euclidean_distance)

		if i == 2:
				
			# Used for get_angle_factor
			

			if type(hitobject_list[-1]) == circle or (type(hitobject_list[-1]) == slider and not hitobject_list[-1].movement):
				delta_distance_factor = get_delta_distance_factor(hitobject.euclidean_distance, hitobject_list[-1].euclidean_distance)

				if type(hitobject_list[-1]) == circle:
					x2, y2 = hitobject_list[-1].x, hitobject_list[-1].y
				else:
					x2, y2 = hitobject_list[-1].x_start, hitobject_list[-1].y_start

				if type(hitobject_list[-2]) == circle:
					x3, y3 = hitobject_list[-2].x, hitobject_list[-2].y
				elif type(hitobject_list[-2]) == slider and not hitobject_list[-1].movement:
					x3, y3 = hitobject_list[-2].x_start, hitobject_list[-2].y_start
				else:
					x3, y3 = hitobject_list[-2].x_end, hitobject_list[-2].y_end
				
				angle_factor = get_angle_factor(x1, y1, x2, y2, x3, y3, hitobject_list)
						

			else:
				# placeholders since I don't think this factor matters if the previous hitobject is a slider that requires movement
				delta_distance_factor = 1

				x2, y2, x3, y3 = hitobject_list[-1].x_end, hitobject_list[-1].y_end, hitobject_list[-1].x_start, hitobject_list[-1].y_start

				angle_factor = get_angle_factor(x1, y1, x2, y2, x3, y3, hitobject_list)

		# stack factor preparation
		if type(hitobject_list[i]) == circle:
			if (x1, y1) == (hitobject_list[i].x, hitobject_list[i].y):
				stack_ms = object_timestamp - hitobject_list[i].timestamp
				stack_index = i
				stack_type = "circle"

		else:
			if (x1, y1) == (hitobject_list[i].x_end, hitobject_list[i].y_end):
				stack_ms = object_timestamp - hitobject_list[i].timestamp_end
				stack_index = i
				stack_type = "sliderend"

			if (x1, y1) == (hitobject_list[i].x_start, hitobject_list[i].y_start):
				stack_ms = object_timestamp - hitobject_list[i].timestamp_start
				stack_index = i
				stack_type = "sliderstart"
			
	stack_factor = get_stack_factor(stack_ms, circle, stack_type)

	density = distance_factor * delta_distance_factor * angle_factor * stack_factor
	return hitobject, density



def get_raw_slider(line_stats, hitobject_list, map_ms):
	# Return information about the slider and its raw density
	pass

def get_hitobject_type(line_stats):
	
	hitobject_num = int(line_stats[3])
    
	# Rule out inclusion of spinners in data
	if hitobject_num == 12:
		return "spinner"
	
	else:
		if bin(hitobject_num).endswith('1'):
			return "circle"
		else:
			return "slider"

def get_frame_densities(map, map_ms):
	
	# First get to where hit objects begin
	for line in map:
		if line.startswith('[HitObjects]'):
			# print(line.replace('[HitObjects]', 'e'))
			break
	
	# The functions that get density will need to access data about previous hitobjects, hence this list
	hitobject_list = []

	# Hit object data mining begins here
	for line in map:

		line_stats = line.split

		hitobject_type = get_hitobject_type(line_stats)

		# Exclude spinners from data
		if hitobject_type == "spinner":
			continue

		elif hitobject_type == "circle":
			hitobject, density,  = get_raw_circle(line_stats, hitobject_list, map_ms)

		else:
			hitobject, density = get_raw_slider(line_stats, hitobject_list, map_ms)

		hitobject_list.append(hitobject)

def start_new_map(file_path, new_ar):
	map = open(file_path, "r", encoding="utf-8")
	ar = float(get_original_ar(map))
	map.seek(0)  # Resets line variable for next instance of 'for line in map'

	if new_ar == "EZ":
		# Easy (EZ) mod cuts AR in half
		ar = ar * 0.5

	elif new_ar == "HR":
		# Hardrock (HR) mod multiplies AR by 1.4 up to a maximum of 10
		if (ar * 1.4) > 10:
			ar = 10
		else:
			ar = ar * 1.4

	elif new_ar != "NM":
		# For if user wishes to simulate readability with a new AR.
		# new_ar must be within the AR range zero to 11
		if (0 <= float(new_ar) <= 11):
			ar = new_ar
		# When making GUI, add blockage that simulates this requirement

		map_ms = ar_to_ms(ar)

	frame_densities = get_frame_densities(map, map_ms)
