



LOCAL_DIR = "/home/ammar/Downloads/terrain_maps/"
REMOTE_TMAP_DIR = "/var/opt/built/save_on_request_maps/"


import os
from pybuilt.util import bash_ifc
import ipdb



def _get_files_on_local():
	return os.listdir(LOCAL_DIR)



def _get_files_on_remote(machine):
	with bash_ifc.BashIfc(machine) as billy_ifc:
		file_names, _ = billy_ifc.exec_cmd('ls {}'.format(REMOTE_TMAP_DIR), echo_cmd=True, print_output=False)
	return file_names
	

def _copy_file_to_local(machine, from_path, to_path):
	exit_code = bash_ifc.BashIfc(machine).scp_from(machine, from_path, to_path, print_output=True)
	if not exit_code:
		print('Successfully copied file {}'.format(from_path))
	else:
		print('Failed to copy file {}'.format(from_path))

local_files = _get_files_on_local()
remote_files = _get_files_on_remote('10.100.0.13')

for file in remote_files:
	if file in local_files:
		print('File present so skipping: {}'.format(file))
		continue
	_copy_file_to_local('10.100.0.13', REMOTE_TMAP_DIR + file, LOCAL_DIR + file)



