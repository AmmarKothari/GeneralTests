import io
import pdb
import re
import datetime
import glob
import click
import os

# DUMP_PTS_FN = 'ex_dump_pts.txt'
# TERRAIN_MAP_PTS_FN = 'terrain_map_update_pts.txt'
EX_DUMP_LOGS = glob.glob('ex_dump.log*')
EXCAVATE_VOLUME_LOGS = glob.glob('excavate_volume.log*')

fns = EX_DUMP_LOGS + EXCAVATE_VOLUME_LOGS

DEFAULT_OUTPUT_FN = 'combined_logs.txt'

logging_regex = '\d\d-\d\d-\d\d \d\d:\d\d:\d\d.\d\d\d'
logging_datetime_format = '%y-%m-%d %H:%M:%S.%f'

input_datetime_format = '%Y:%m:%d:%H:%M:%S'

def datetime_sorting_func(line):
	return datetime.datetime.strptime(re.search(logging_regex, line).group(0), logging_datetime_format)

def is_valid_line(line):
	try:
		datetime_sorting_func(line)
	except AttributeError:
		return False
	except ValueError:
		return False
	return True

def get_fns_from_inputs(input_fns):
	fns = []
	for input_fn in input_fns:
		fns.extend(glob.glob(input_fn))

	print("Opening data from the following files:\n{}".format("\n".join(fns)))
	return fns

def get_all_lines(fns):
	all_lines = []
	for fn in fns:
		with io.open(fn) as raw_file:
			for line in raw_file:
				if is_valid_line(line):
					all_lines.append(line)
	print("Total number of lines: {}".format(len(all_lines)))
	return all_lines

def write_output(sorted_lines, output_fn, range_time):
	with io.open(os.path.expanduser(output_fn), mode='w') as output_file:
		for line in sorted_lines:
			line_time = datetime_sorting_func(line)
			# only write if within range
			if line_time >= range_time[0] and line_time <= range_time[1]:
				output_file.write(line)

def parse_time_range(time_range_str):
	range_str = time_range_str.split('-')
	range_time_obj = [datetime.datetime.strptime(time_str, input_datetime_format) for time_str in range_str]
	return range_time_obj

def remove_duplicate_lines(sorted_lines):
	duplicate_line_indexes = []
	for i in range(len(sorted_lines)-1):
		if sorted_lines[i] == sorted_lines[i+1]:
			duplicate_line_indexes.append(i)
	print('Removing {} duplicate lines'.format(len(duplicate_line_indexes)))
	for i in reversed(duplicate_line_indexes):
		sorted_lines.pop(i)
	return sorted_lines


@click.command()
@click.argument('input_fns', nargs=-1, type=click.Path(exists=True))
@click.option('--output_filename', default=DEFAULT_OUTPUT_FN, help='Name of output file')
@click.option('--time_range', default=None, help='Only include values that fall within time range.  Example: 2019:11:20:11:00:00-2019:11:20:12:00:00')
@click.option('-no_duplicates', is_flag=True)
def combine_logs(input_fns, output_filename, time_range, no_duplicates):
	fns = get_fns_from_inputs(input_fns)
	all_lines = get_all_lines(fns)
	sorted_lines = sorted(all_lines, key=datetime_sorting_func)
	if time_range is None:
		# get the range from the first and last message of the lines
		start_time = datetime_sorting_func(sorted_lines[0])
		end_time = datetime_sorting_func(sorted_lines[-1])
		time_range = '{}-{}'.format(start_time.strftime(input_datetime_format), end_time.strftime(input_datetime_format))
	range_time = parse_time_range(time_range)
	if no_duplicates:
		sorted_lines = remove_duplicate_lines(sorted_lines)
	write_output(sorted_lines, output_filename, range_time)


if __name__ == '__main__':
	combine_logs()

