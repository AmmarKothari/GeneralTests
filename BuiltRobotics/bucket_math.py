import matplotlib.pyplot as pyplot
import numpy as np

# # from ali's spec
# BUCKET_DEPTH=2.20  # guess from manual
# BUCKET_LENGTH=2.02
# BUCKET_LINK_TO_BUCKET_TIP_ANGLE=1.05

# from billy's spec
BUCKET_DEPTH=2.20  # guess from manual - copied
BUCKET_LENGTH=2.092
BUCKET_LINK_TO_BUCKET_TIP_ANGLE=1.03



# angle across from that side
bucket_depth_angle = BUCKET_LINK_TO_BUCKET_TIP_ANGLE
bucket_length_angle = np.arcsin(np.sin(bucket_depth_angle) / BUCKET_DEPTH * BUCKET_LENGTH)
bucket_back_angle = np.pi - bucket_depth_angle - bucket_length_angle

# bucket back length
# bucket_back_length = np.sqrt(BUCKET_LENGTH**2 + BUCKET_DEPTH**2 - 2*BUCKET_LENGTH*BUCKET_DEPTH*np.cos(bucket_back_angle))
bucket_back_length = BUCKET_DEPTH / np.sin(bucket_depth_angle) * np.sin(bucket_back_angle)

# put the bucket bottom along (x = 0)
plt.plot([0, BUCKET_DEPTH], [0, 0], 'rx-')

# add the part from the bucket teeth to the bucket joint
plt.plot([BUCKET_DEPTH, BUCKET_DEPTH - np.cos(bucket_back_angle) * BUCKET_LENGTH], [0, np.sin(bucket_back_angle) * BUCKET_LENGTH], 'bx:')

# add back of the bucket
plt.plot([0, bucket_back_length * np.cos(bucket_length_angle)], [0, bucket_back_length * np.sin(bucket_length_angle)], 'kx-')

plt.show()