PAD_DEPTH = 0.1524 # m
VPAT_CAPACITY = 4.64 #m^3 -> 6.07 yard^3
VPAT_WIDTH = 4.17576 # m -> 13.7 ft

PUSH_SPEED = 0.5 # m/s
REVERSE_SPEED = 1.0 # m/s

FOUNDATION_DIAMETER = 2*160 * 12 * 2.54 / 100  # foundation diameter at bottom in m

IDEAL_PUSH_DIST = VPAT_CAPACITY / (PAD_DEPTH * VPAT_WIDTH) # m