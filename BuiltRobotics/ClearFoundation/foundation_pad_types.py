# Just a bunch of functions that evaluate different types of pads

import pdb

import argparse

from foundation import foundation
from evaluate_pads import evaluate_pads

import matplotlib.pyplot as plt
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED, FOUNDATION_DIAMETER


### All classes for creating a set of polygons given a polygon area to grade
from enclosing_rectangle_pads import enclosing_rectangle_pads
from enclosing_polygon_pads import enclosing_polygon_pads
from sequential_rectangles_pads import sequential_rectangles_pads
from optimize_foundation_pads import optimize_foundation_pads
FUNC_DICT = {
	'enclosing_rectangle': enclosing_rectangle_pads,
	'enclosing_polygon': enclosing_polygon_pads,
	'sequential_rectangles': sequential_rectangles_pads,
	'optmiize': optimize_foundation_pads
}









if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Evaluate different pad structures for foundation')
	parser.add_argument('padfunc', type=str, help='name of method to generate pads')
	parser.add_argument('--sides', required=False, default=9, help='number of sides for a polygon.  Only needed for enclosing polygon')

	args = parser.parse_args()
	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	pads_generator = FUNC_DICT[args.padfunc](f1.poly).gen_foundation_pads(args.sides)
	ep = evaluate_pads(pads_generator, f1.poly)
	process_dict, unprocessed_area = ep.evaluate_pads()
	grading_stats = ep.grading_process_stats(process_dict, unprocessed_area)
	score = ep.grading_score(process_dict, grading_stats)
	print('Score: {}'.format(score))
	pdb.set_trace()


