


COUNT_DOWN = 10

mock_points = "1,2,3.4,n,5, 6, 7.8, e\n\
1,2,3.4,n,5, 6, 7.9,e\n\
1,2,3.4,n,5, 6, 7.10,e"

# ------------------
# Non-flask operations
# ------------------
def setup_recording(fn=None):
	# type: str -> None
	# if filename exists, add date and time to it

	# else create file
	pass


def record_lle_point(fn=None):
	# type: str -> None
	# open file with csv writer

	# write points in correct format
	pass

def get_lle_points(fn=None):
	# type: (str) -> List[str]
	return mock_points.split('\n')

def load_lle_points(fn=None):
	# type: (str) -> dict
	# open file with csv reader

	# format points into a dictionary
	lines = get_lle_points()
	points = []
	for line in lines:
		parts = line.split(',')
		point = {'lat': {'h': parts[0], 'm': parts[1], 's':parts[2], 'dir': parts[3]},
				 'lon': {'h': parts[4], 'm': parts[5], 's':parts[6], 'dir': parts[7]}
				 }
	 	points.append(point)
 	print(points)
	return points

def fix_status():
	return 'True'