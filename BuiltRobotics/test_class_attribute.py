class Gears(object):
	gear = 0

	def __init__(self):
		pass

	def increase_gear(self):
		Gears.gear += 1

	def decrease_gear(self):
		Gears.gear -= 1

	def print_gear(self):
		print("Current Gear: {}".format(Gears.gear))



if __name__ == '__main__':
	G1 = Gears()
	G1.increase_gear()
	G1.print_gear()
	G2 = Gears()
	G2.print_gear()