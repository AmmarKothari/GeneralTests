# replace a string in file
# when calling from command line
# first argument is file that needs strings replaced
# second argument is current string
# third string is the string to replace with





import sys, os
import pdb

fn = sys.argv[1]
cur_str = sys.argv[2]
new_str = sys.argv[3]

# read file
with open(fn, 'rb') as f:
	content = f.read()
	# content = f.readlines()

# replace strings
new_content = content.replace(cur_str, new_str)


# write file
new_fn = list(os.path.split(fn))
new_fn[1] = '_'.join(['test',new_fn[1]])
new_fn = os.path.join(*new_fn)
with open(fn, 'w') as f:
	f.write(new_content)


