import numpy as np

class circle:
	def __init__(self, timestamp, x, y, euclidean_distance, angle):
		self.timestamp = timestamp
		self.x = x
		self.y = y
		self.euclidean_distance = euclidean_distance
		self.angle = angle

class slider:
	def __init__(self, timestamp_start, timestamp_end, x_start, y_start, x_end, y_end, complexity, raw_cluster, euclidean_distance, angle):
		self.timestamp_start = timestamp_start
		self.timestamp_end = timestamp_end
		self.x_start = x_start
		self.y_start = y_start
		self.x_end = x_end
		self.y_end = y_end
		self.complexity = complexity
		self.raw_cluster = raw_cluster
		self.euclidean_distance = euclidean_distance
		self.angle = angle

class timingPoint:
	def __init__(self, timestamp, beat_length):
		self.timestamp = timestamp
		self.beat_length = beat_length


def get_distance_factor(x1, y1, x2, y2):
	# "1" indicates current hitobject, "2" indicates previous.
	euclidean_distance = (np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2))

	# handles case of hitobjects being stacked back-to-back and prevent divide by zero in log10
	if euclidean_distance == 0:
		return 1, 0
	
	distance_factor = ((np.log10(euclidean_distance / 10) / 3) + 0.595)

	return distance_factor, euclidean_distance


def get_delta_distance_factor(d1, d2):
	# "1" indicates current hitobject, "2" indicates previous.
	difference = d1 - d2
	if difference > 0:
		return ((np.log10(difference + 170) / 10 ) / 3) + 0.595
	else:
		# for if the difference is negative, i.e. a deccelerating stream
		return ((np.log10(np.abs(difference) + 340) / 10 ) / 4) + 0.595
	

def get_slope(a1, b1, a2, b2):
	try:
		return (b2 - b1) / (a2 - a1)
	except:
			if b2 - b1 > 0:
				return float("inf")
			elif b2 - b1 < 0:
				return float("-inf")
			else: # Same coordinates in this case
				return "no angle"
			

def get_orientation(slope1, slope2, x1, y1, x2, y2, x3, y3):

	if slope1 == slope2 and slope1 != float("inf") and slope1 != float("-inf"):



		if x1 < x2:

			if x2 < x3:
				return "collinear-straight"
			else:
				return "collinear-reverse"
				
		else:
			if x2 > x3:
				return "collinear-straight"
			else:
				return "collinear-reverse"


	
	y_int = y3 - slope2 * x3

	if slope2 > 0:

	# y = slope2 * x + y_int
	# y = mx + b

		if slope2 != float("inf"):

			
		# y > mx + b
			if x3 < x2:

				if y1 > slope2 * x1 + y_int:
					return "counterclockwise"
				else:
					return "clockwise"
				
			else:
				if y1 < slope2 * x1 + y_int:
					return "counterclockwise"
				else:
					return "clockwise"

			
		else:
			if x3 > x1:
				return "counterclockwise"
			elif x3 < x1:
				return "clockwise"
			else:
				if y1 > y2:
					return "collinear-straight"
				else:
					return "collinear-reverse"

	elif slope2 < 0:

		if slope2 != float("-inf"):

			if x3 > x2:

				if y1 < slope2 * x1 + y_int:
					return "counterclockwise"
				else:
					return "clockwise"
				
			else:
				if y1 > slope2 * x1 + y_int:
					return "counterclockwise"
				else:
					return "clockwise"
		
		else:
			if x3 < x1:
				return "counterclockwise"
			elif x3 > x1:
				return "clockwise"
			else:
				if y1 < y2:
					return "collinear-straight"
				else:
					return "collinear-reverse"
				
	else: # slope2 == 0

		if x3 < x2:

			if y1 > y3:
				return "counterclockwise"
			elif y1 < y3:
				return "clockwise"
			else:
				if x1 > x2:
					return "collinear-straight"
				else:
					return "collinear-reverse"
				
		else:
			if y1 < y3:
				return "counterclockwise"
			elif y1 > y3:
				return "clockwise"
			else:
				if x1 < x2:
					return "collinear-straight"
				else:
					return "collinear-reverse"

		
def get_angle_factor(x1, y1, object_range):

	# It has come to my attention that osu!'s playfield of game pixels is organized in a way
	# such that x increases going right, and y increases going down.
	# https://osu.ppy.sh/wiki/en/Client/Playfield
	# The following code was written with a standard coordinate plane in mind, with y increasing going up,
	# following math principles. Hence, "counterclockwise" and "clockwise" should technically be swapped.
	# But, ya know, if it ain't broke, don't fix it !!

	if type(hitobject_list[-1]) == circle:
		x2, y2 = hitobject_list[-1].x, hitobject_list[-1].y

		slope1 = get_slope(x1, y1, x2, y2)


		if type(hitobject_list[-2]) == circle:
			x3, y3 = hitobject_list[-2].x, hitobject_list[-2].y
		else:
			x3, y3 = hitobject_list[-2].x_end, hitobject_list[-2].y_end

		slope2 = get_slope(x2, y2, x3, y3)

		if slope1 == "no angle" or slope2 == "no angle":
			return 1, 0
		
		orientation = get_orientation(slope1, slope2, x1, y1, x2, y2, x3, y3)

	elif type(hitobject_list[-1]) == slider and not hitobject_list[-1].complexity:
		# Dealing with previous object being a non-complex slider,
		# so we're finding a new point (x2, y2) where the vectors intersect
		x2_end, y2_end = hitobject_list[-1].x_end, hitobject_list[-1].y_end
		
		slope1 = get_slope(x1, y1, x2_end, y2_end)

		x2_start, y2_start = hitobject_list[-1].x_start, hitobject_list[-1].y_start

		if type(hitobject_list[-2]) == circle:
			x3, y3 = hitobject_list[-2].x, hitobject_list[-2].y
		else:
			x3, y3 = hitobject_list[-2].x_end, hitobject_list[-2].y_end

		slope2 = get_slope(x2_start, y2_start, x3, y3)

		if slope1 == "no angle" or slope2 == "no angle":
			return 1, 0

		# https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
		# Just basic algebra here that's been supercompressed
		y_int1 = y1 - slope1 * x1
		y_int2 = y3 - slope2 * x3

		try:
			x2 = (y_int2 - y_int1) / (slope1 - slope2)
			y2 = slope1 * x2 + y_int1
		except:
			x2, y2 = hitobject_list[-1].x_start, hitobject_list[-1].y_start
		
		if np.isnan(x2) or np.isnan(y2):
			x2, y2 = hitobject_list[-1].x_start, hitobject_list[-1].y_start

		orientation = get_orientation(slope1, slope2, x1, y1, x2, y2, x3, y3)

	if orientation == "collinear-straight":
		angle = 0

	elif orientation == "collinear-reverse":
		angle = np.pi

	else:
		# Angle between two vectors
		# I copied this from somewhere. Don't ask me how it works. It just does.
		a = np.array([x1, y1])
		b = np.array([x2, y2])
		c = np.array([x3, y3])

		ba = a - b
		bc = c - b

		cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))

		# subtract from 180 to convert angle between vectors to the angle in which cursor movement changes
		angle = np.pi - np.arccos(cosine_angle)

		if np.isnan(angle):
			angle = 0

		if orientation == "clockwise":
			angle = -angle

	valid_third_previous = object_range >= 3 and (type(hitobject_list[-3]) == circle or (type(hitobject_list[-3]) == slider and not hitobject_list[-3].complexity))

	if np.sign(angle) != np.sign(hitobject_list[-1].angle) and valid_third_previous:
		# Check if previous angle exists at the same time as current and is opposite
		resulting = np.abs(angle) + np.abs(hitobject_list[-1].angle)
	else:
		resulting = np.abs(angle)

	return (np.sin(resulting / 485.5)) ** 0.34 + 1, angle


def in_stack(current_timestamp, previous_timestamp):
	stack_window = map_ms * stack_leniency
	if current_timestamp - previous_timestamp <= stack_window:
		return True
	else:
		return False


def get_obscurity_factor(timestamp, obscurity_ms, obscurity_type):

	coverage = (map_ms - (timestamp - obscurity_ms)) / map_ms
	
	if obscurity_type == 1:
		return np.log10(5 * coverage + 2) + 0.8
	elif obscurity_type == 2:
		return np.log10(4 * coverage + 2) + 0.8
	elif obscurity_type == 3:
		return np.log10(5 * coverage + 2) + 1
	elif obscurity_type == 4:
		return np.log10(5 * coverage + 2) + 0.8
	else:
		pass


def get_object_range(object_timestamp):

	if len(hitobject_list) == 0:
		return 0
	
	in_view = 0
	for i in range(len(hitobject_list) - 1, -1, -1):
	#  Last possible iteration is i = 0, which is the first index of hitobject_list

		if type(hitobject_list[i]) == circle:
			if object_timestamp - hitobject_list[i].timestamp <= map_ms:
				in_view += 1

		else:  # Is basically the same as the if statement above, but accounts for slider attribute name
			if object_timestamp - hitobject_list[i].timestamp_end <= map_ms:
				in_view += 1

	return in_view


def get_raw_circle(line_stats):
	# Return information about the circle and its raw density

	# Parsing circle information
	x1 = int(line_stats[0])
	y1 = int(line_stats[1])
	object_timestamp = int(line_stats[2])

	# Last two attributes are euclidean distance and angle. 0 is a placeholder that will be replaced if necessary.
	hitobject = circle(object_timestamp, x1, y1, 0, 0)
	object_range = get_object_range(object_timestamp)

	# For if there are no other hitobjects in view before current hitobject
	if object_range == 0:
		raw_density = 0  # A lonely circle on the screen is the easiest to read, hence density 0
		return hitobject, raw_density

	distance_factor = 1
	delta_distance_factor = 1
	angle_factor = 1
	obscurity_factor = 1

	current_stack = 0
	obscurity_type = -1

	for i in range(1, (object_range + 1)):

		if i == 1:
			if type(hitobject_list[-1]) == circle:
				distance_factor, euclidean_distance = get_distance_factor(x1, y1, hitobject_list[-1].x, hitobject_list[-1].y)

			else:
				distance_factor, euclidean_distance = get_distance_factor(x1, y1, hitobject_list[-1].x_end, hitobject_list[-1].y_end)
				
			setattr(hitobject, "euclidean_distance", euclidean_distance)


		if i == 2:
				
			if type(hitobject_list[-1]) == circle or (type(hitobject_list[-1]) == slider and not hitobject_list[-1].complexity):

				delta_distance_factor = get_delta_distance_factor(hitobject.euclidean_distance, hitobject_list[-1].euclidean_distance)
				angle_factor, angle = get_angle_factor(x1, y1, object_range)

				setattr(hitobject, "angle", angle)


		# Finding the source of obscurity (if any) that is closest to the current timestamp
		if type(hitobject_list[-i]) == circle and (hitobject_list[-i].x, hitobject_list[-i].y) == (x1, y1) and obscurity_type == -1:
			
			if i >= 2:

				if current_stack > 0:
					pass

				else:
					obscurity_ms = hitobject_list[-i].timestamp
					obscurity_type = 1

			elif i == 1 and in_stack(object_timestamp, hitobject_list[-i].timestamp):
				current_stack += 1

			else: # Circles are on same coordinates but not stacked
				obscurity_ms = hitobject_list[-i].timestamp
				obscurity_type = 1

		if type(hitobject_list[-i]) == slider and (hitobject_list[-i].x_start, hitobject_list[-i].y_start) == (x1, y1) and obscurity_type == -1:

			obscurity_ms = hitobject_list[-i].timestamp_start
			obscurity_type = 1
			
	try:
		obscurity_factor = get_obscurity_factor(object_timestamp, obscurity_ms, obscurity_type)
	except:
		pass

	density = distance_factor * delta_distance_factor * (angle_factor ** (1 / distance_factor)) * obscurity_factor
	return hitobject, density


def get_length_factor(length):
	return np.cbrt(length ** 0.2)


def get_box_factor(slider_x_coords, slider_y_coords):
	x_coords_sorted = np.sort(slider_x_coords)[::-1]
	y_coords_sorted = np.sort(slider_y_coords)[::-1]

	x_highest = x_coords_sorted[0]
	x_lowest = x_coords_sorted[-1]
	y_highest = y_coords_sorted[0]
	y_lowest = y_coords_sorted[-1]

	# Largest possible hypotenuse is 640
	hypotenuse = np.sqrt((x_highest - x_lowest) ** 2 + (y_highest - y_lowest) ** 2)
	
	return np.cbrt(hypotenuse ** 0.2), hypotenuse


def get_end_timestamp(length, timestamp_start, slides):
	index = 0
	velocity = 1

	while True:
		try:
			tp_timestamp = timing_points[index].timestamp
		except:
			break

		if tp_timestamp > timestamp_start:
			break
		num = timing_points[index].beat_length

		if num < 0:
			velocity = num
		else:
			beat_length = num

		index += 1

	if velocity < 0:
		velocity_multiplier = -1 / (velocity / 100)
		completion_time = length / (slider_multiplier * 100 * velocity_multiplier) * beat_length * slides
	else:
		completion_time = length / (slider_multiplier * 100) * beat_length * slides

	return timestamp_start + completion_time


def get_complexity(hypotenuse, slides):
	if hypotenuse <= 100 and slides == 1:
		return False
	else:
		return True


def get_raw_slider(line_stats):
	# Return information about the slider and its raw density

	# Parsing slider information
	x_start = int(line_stats[0])
	y_start = int(line_stats[1])
	timestamp_start = int(line_stats[2])
	raw_cluster = str(line_stats[5])
	slides = int(line_stats[6])
	length = float(line_stats[7])

	stored_cluster = raw_cluster.split("|")
	stored_cluster.pop(0) # Takes out the first index, which is the letter representing slider type (bezier, catmull, etc)
	curve_cluster = stored_cluster
	slider_x_coords = np.array(x_start)
	slider_y_coords = np.array(y_start)

	for i in range(len(curve_cluster)):
		curve_point = curve_cluster[i].split(":")
		slider_x_coords = np.append(slider_x_coords, int(curve_point[0]))
		slider_y_coords = np.append(slider_y_coords, int(curve_point[1]))

	x_end = int(curve_point[0])
	y_end = int(curve_point[1])

	distance_factor = 1
	delta_distance_factor = 1
	angle_factor = 1
	obscurity_factor = 1

	euclidean_distance = 0
	angle = 0

	length_factor = get_length_factor(length)
	box_factor, hypotenuse = get_box_factor(slider_x_coords, slider_y_coords)

	object_range = get_object_range(timestamp_start)

	timestamp_end = get_end_timestamp(length, timestamp_start, slides)

	# if even number of slides, then the actual end of the slider would be the starting coords
	if slides % 2 == 0:
		x_end, y_end = x_start, y_start

	complexity = get_complexity(hypotenuse, slides)

	# For if there are no other hitobjects in view before current hitobject
	if object_range == 0:
		raw_density = 0  # A lonely slider on the screen is the easiest to read, hence density 0
		hitobject = slider(timestamp_start, timestamp_end, x_start, y_start, x_end, y_end, complexity, stored_cluster, euclidean_distance, angle)
		return hitobject, raw_density

	current_stack = 0
	obscurity_type = -1

	for i in range(1, (object_range + 1)):

		if i == 1:
			if type(hitobject_list[-1]) == circle:
				distance_factor, euclidean_distance = get_distance_factor(x_start, y_start, hitobject_list[-1].x, hitobject_list[-1].y)

			else:
				distance_factor, euclidean_distance = get_distance_factor(x_start, y_start, hitobject_list[-1].x_end, hitobject_list[-1].y_end)

		if i == 2:
			if type(hitobject_list[-1]) == circle or (type(hitobject_list[-1]) == slider and not hitobject_list[-1].complexity):

				delta_distance_factor = get_delta_distance_factor(euclidean_distance, hitobject_list[-1].euclidean_distance)
				angle_factor, angle = get_angle_factor(x_start, y_start, object_range)

		# Finding the source of obscurity (if any) that is closest to the current timestamp
		if type(hitobject_list[-i]) == circle and (hitobject_list[-i].x, hitobject_list[-i].y) == (x_start, y_start) and not (obscurity_type == -1):
			
			if i >= 2:

				if current_stack > 0:
					pass

				else:
					obscurity_ms = hitobject_list[-i].timestamp
					obscurity_type = 1

			elif i == 1 and in_stack(timestamp_start, hitobject_list[-i].timestamp):
				current_stack += 1

			else: # Circle is on same coordinates as slider start, but not stacked
				obscurity_ms = hitobject_list[-i].timestamp
				obscurity_type = 1

		if type(hitobject_list[-i]) == slider and (hitobject_list[-i].x_start, hitobject_list[-i].y_start) == (x_start, y_start) and not (obscurity_type == -1):

			# Signifies slider obscured by identical slider
			if raw_cluster == hitobject_list[-i].stored_cluster:
				obscurity_type = 3
			elif raw_cluster == (hitobject_list[-i].stored_cluster)[::-1]:
				obscurity_type = 4
			else:
				obscurity_type = 2

			obscurity_ms = hitobject_list[-i].timestamp_start

	try:
		obscurity_factor = get_obscurity_factor(timestamp_start, obscurity_ms, obscurity_type)
	except:
		pass

	hitobject = slider(timestamp_start, timestamp_end, x_start, y_start, x_end, y_end, complexity, stored_cluster, euclidean_distance, angle)

	density = distance_factor * delta_distance_factor * (angle_factor ** (1 / distance_factor)) * obscurity_factor * (length_factor * box_factor ** (length_factor)) ** (np.log10(slides * 0.2) + 1.7)

	return hitobject, density


def get_hitobject_type(line_stats):
	
	hitobject_num = int(line_stats[3])

	# Rule out inclusion of spinners in data
	if hitobject_num == 12:
		return "spinner"
	
	else:
		if bin(hitobject_num).endswith("1"):
			return "circle"
		else:
			return "slider"


def get_frame_densities(map):
	
	# Get to where timing points begin
	for line in map:
		if line.startswith("[TimingPoints]"):
			break

	global timing_points
	timing_points = []

	# Timing point info gathering begins here
	for line in map:

		line_stats = line.split(",")

		try:
			timing_points.append(timingPoint(int(line_stats[0]), float(line_stats[1])))
		except:
			break

	# Get to where hit objects begin
	for line in map:
		if line.startswith("[HitObjects]"):
			break
	
	# The functions that get density factors will need to access data about previous hitobjects, hence this list
	global hitobject_list
	hitobject_list = []

	# Hit object info gathering begins here
	for line in map:

		line_stats = line.split(",")

		hitobject_type = get_hitobject_type(line_stats)

		# Exclude spinners from data
		if hitobject_type == "spinner":
			continue

		elif hitobject_type == "circle":
			hitobject, density,  = get_raw_circle(line_stats)

		else:
			hitobject, density = get_raw_slider(line_stats)

		hitobject_list.append(hitobject)
		try: 
			raw_densities = np.append(raw_densities, density)
		except:
			raw_densities = np.array([density])

	# initialize frame_densities with the very first hitobject
	frame_densities = np.array([raw_densities[0]])

	for i in range(1, len(raw_densities)):

		frame = raw_densities[i]
		object_range = 0
		try:
			current_ms = hitobject_list[i].timestamp
			
		except:
			current_ms = hitobject_list[i].timestamp_start

		while True:
			object_range += 1
			if i-object_range < 0:
				break

			try:
				previous_ms = hitobject_list[i-object_range].timestamp
			
			except:
				previous_ms = hitobject_list[i-object_range].timestamp_end
			
			if not (current_ms - previous_ms <= map_ms):
				break

			if raw_densities[i-object_range] > 1:
				frame += raw_densities[i-object_range] ** (np.sqrt((map_ms - (current_ms - previous_ms)) / map_ms))
			else:
				frame += raw_densities[i-object_range] * (np.sqrt((map_ms - (current_ms - previous_ms)) / map_ms))
			
		frame_densities = np.append(frame_densities, frame)

	return frame_densities


def get_readability_rating(sorted_frame_densities):
	readability_rating = 0

	for i, frame in enumerate(sorted_frame_densities):
		readability_rating += frame * (0.95 ** i)

	return readability_rating


def get_map_details(map):
	for line in map:

		if line.startswith("StackLeniency"):
			stack_leniency = float(line.replace("StackLeniency:", ""))

		if line.startswith("Mode"):
			mode = int(line.replace("Mode:", ""))

		if line.startswith("ApproachRate"):
			ar = float(line.replace("ApproachRate:", ""))

		if line.startswith("SliderMultiplier"):
			slider_multiplier = float(line.replace("SliderMultiplier:", "")) 
			
	return stack_leniency, mode, ar, slider_multiplier


def ar_to_ms(ar):
	# https://osu.ppy.sh/wiki/en/Beatmap/Approach_rate
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


def start_new_map(file_path, new_ar):
	map = open(file_path, "r", encoding="utf-8")

	try:
		global stack_leniency, slider_multiplier
		stack_leniency, mode, ar, slider_multiplier = (get_map_details(map))
	except:
		return "error reading .osu file. is this a .osu file?"
	

	if mode != 0:
		return "not a standard beatmap"
	
	map.seek(0)  # Resets line variable for next instance of "for line in map"

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

	global map_ms
	map_ms = ar_to_ms(ar)

	frame_densities = get_frame_densities(map)

	return get_readability_rating(np.sort(frame_densities)[::-1])