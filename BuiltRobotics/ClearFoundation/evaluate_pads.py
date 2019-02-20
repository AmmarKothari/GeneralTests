from ammar_super import AmmarSuper
from foundation import foundation
from enclosing_rectangle_pads import enclosing_rectangle_pads
import copy
import numpy as np
import pdb
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED, FOUNDATION_DIAMETER
from helper_funcs import linear_interp_between_pts


class evaluate_pads(AmmarSuper):
	def __init__(self, pads, coverage_area):
		self.pads = pads
		self.coverage_area = coverage_area
		self.evaluate_pads()

	def evaluate_pads(self):
		num_pads = len(self.pads)
		process_dict = dict()
		unprocessed_pad = copy.deepcopy(self.coverage_area)
		for i_pad, pad in enumerate(self.pads):
			operation_dict = dict()
			operation_dict['pad'] = pad
			operation_dict['length'] = pad.l
			operation_dict['width'] = pad.w
			operation_dict['material_moved'] = pad.l * pad.w * PAD_DEPTH
			operation_dict['num_lanes'] = np.ceil(pad.w / VPAT_WIDTH)
			operation_dict['pushes_per_lane'] = np.ceil(
				pad.l * PAD_DEPTH * VPAT_WIDTH / VPAT_CAPACITY)
			operation_dict['push_start_locs'] = linear_interp_between_pts(
				pad.front_center, pad.back_center, operation_dict['pushes_per_lane'])
			operation_dict['dirt_length_per_push'] = pad.l / \
				operation_dict['pushes_per_lane'] * operation_dict['num_lanes']
			total_push_dist = 0
			for i_push, push in enumerate(np.arange(operation_dict['pushes_per_lane'])):
				total_push_dist += i_push * \
					operation_dict['dirt_length_per_push']
			operation_dict['total_push_dist'] = total_push_dist
			operation_dict['lane_time'] = operation_dict[
				'total_push_dist'] / PUSH_SPEED + operation_dict['total_push_dist'] / REVERSE_SPEED
			on_foundation_lane = pad.poly.intersection(self.coverage_area)
			operation_dict['area_foundation_cleared'] = on_foundation_lane.area
			operation_dict['area_outside_foundation'] = pad.poly.difference(
				self.coverage_area).area
			newly_graded_area = unprocessed_pad.area - \
				unprocessed_pad.difference(on_foundation_lane).area
			operation_dict[
				'area_regraded'] = on_foundation_lane.area - newly_graded_area
			unprocessed_pad = unprocessed_pad.difference(pad.poly)
			process_dict[i_pad] = copy.deepcopy(operation_dict)
		pdb.set_trace()
		return process_dict, unprocessed_pad


if __name__ == '__main__':
	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	erp = enclosing_rectangle_pads(f1.poly)
	simple_pads = erp.gen_foundation_pads()
	simple_pads.draw(ax1)
	ep = evaluate_pads(simple_pads, f1.poly)
