import argparse
import pdb


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('-uy', '--update_yaml', help='Update system.yaml file with new geofence', required=False, default=False, action='store_true')
	parser.add_argument('-i', '--input', help='Input CSV to generate geofence from', required=True, default=False, action='store_const', const='blah_{}'.format(123))
	args = parser.parse_args()
	pdb.set_trace()






if __name__ == '__main__':
	main()