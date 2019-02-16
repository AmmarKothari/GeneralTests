
import sys
import select

def heardEnter():
    i,o,e = select.select([sys.stdin],[],[],0.0001)
    for s in i:
        if s == sys.stdin:
            input = sys.stdin.readline()
            print(input)
            if input.strip('\n') == 'r':
            	print('heard r: {}'.format(input))
            return True
    return False

while True:
	# print('SQ Data')
	if heardEnter():
		print('Enter!')