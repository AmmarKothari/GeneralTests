from ammar_super import AmmarSuper
from foundation import foundation
from enclosing_rectangle_pads import enclosing_rectangle_pads
import copy
import numpy as np
import pdb
import shapely.ops as so
from constants import PAD_DEPTH, VPAT_CAPACITY, VPAT_WIDTH, PUSH_SPEED, REVERSE_SPEED, FOUNDATION_DIAMETER
from helper_funcs import linear_interp_between_pts


COST_MULTIPLIER = {
	'ungraded_area': 10.0
}

class evaluate_pads(AmmarSuper):
	def __init__(self, pads, coverage_area):
		self.pads = pads
		self.coverage_area = coverage_area

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
		return process_dict, unprocessed_pad

	def grading_process_stats(self, process_dict, unprocessed_pad):
		average_length = np.mean([process['length']
								  for process in process_dict.values()])
		average_width = np.mean([process['width']
								 for process in process_dict.values()])
		total_material = np.sum([process['material_moved']
								 for process in process_dict.values()])
		total_time = sum([process['lane_time']
						  for process in process_dict.values()])
		total_regrade = sum([process['area_regraded']
							 for process in process_dict.values()])
		total_lanes = sum([process['num_lanes']
							 for process in process_dict.values()])
		pad_transition_dist = 0
		for i_process in range(1, len(process_dict.values()) - 1):
			pad_transition_dist += np.linalg.norm(process_dict[i_process][
												  'push_start_locs'][-1] - process_dict[i_process + 1]['push_start_locs'][0])
		total_dist = sum([process['total_push_dist']
						  for process in process_dict.values()]) + pad_transition_dist
		total_area = self.coverage_area.area
		grading_stats_dict = {'average_length': average_length, 'average_width': average_width, 'total_material': total_material, 'total_time': total_time, 'total_regrade': total_regrade,
					  'pad_transition_dist': pad_transition_dist, 'total_dist': total_dist, 'total_area': total_area, 'total_lanes': total_lanes,
					  'ungraded_area':unprocessed_pad.area}
		# print('Pad Width: {average_width:.2f} m, Pad Length: {average_length:.2f} m, Total Lanes: {total_lanes:.0f}'.format(**grading_stats_dict))
		# print('Pad Depth: {:.2f} m, Total Material: {:.2f} Ungraded Area: {:.2f}, m^3, Total Dist: {:.2f} (Pad Transition Dist: {:.2f}%), Total Regrade: {:.2f} ({:.2f}%), Estimated Time: {:.0f} sec ({:.2f} min)'.format(
		# 	PAD_DEPTH, total_material, unprocessed_pad.area, total_dist, pad_transition_dist / total_dist * 100, total_regrade, total_regrade / total_area * 100, total_time, total_time / 60))
		# print('Ungraded Area: {:.2f} m^3, Total Regrade: {:.2f} %'.format(unprocessed_pad.area, total_regrade / total_area * 100))
		return grading_stats_dict

	def grading_score(self, process_dict, grading_stats_dict):
		total_graded_poly = so.cascaded_union(
			[p['pad'].poly for p in process_dict.values()])
		total_useful_graded = self.coverage_area.area - \
			self.coverage_area.difference(total_graded_poly).area
		grade_score = - COST_MULTIPLIER['ungraded_area'] * grading_stats_dict['ungraded_area'] \
		- grading_stats_dict['total_regrade'] \
		- grading_stats_dict['total_dist'] + total_useful_graded
		return grade_score


if __name__ == '__main__':
	fig1, ax1 = plt.subplots()
	f1 = foundation(FOUNDATION_DIAMETER / 2)
	erp = enclosing_rectangle_pads(f1.poly)
	simple_pads = erp.gen_foundation_pads()
	simple_pads.draw(ax1)
	ep = evaluate_pads(simple_pads, f1.poly)
	pdb.set_trace()
