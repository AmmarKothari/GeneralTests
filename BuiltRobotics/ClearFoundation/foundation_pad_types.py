# Just a bunch of functions that evaluate different types of pads

import pdb

import argparse
from enclosing_rectangle_pads import enclosing_rectangle_pads
from foundation import foundation
from evaluate_pads import evaluate_pads

import matplotlib.pyplot as plt
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED, FOUNDATION_DIAMETER


FUNC_DICT = {
	'enclosing_rectangle': enclosing_rectangle_pads
}









if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Evaluate different pad structures for foundation')
	parser.add_argument('padfunc', type=str, help='Test string')


	args = parser.parse_args()


	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	pads_generator = FUNC_DICT[args.padfunc](f1.poly).gen_foundation_pads()
	ep = evaluate_pads(pads_generator, f1.poly)
	process_dict, unprocessed_area = ep.evaluate_pads()
	grading_stats = ep.grading_process_stats(process_dict, unprocessed_area)
	pdb.set_trace()