import cv2
import time
import ipdb

ORIGINAL_VIDEO = '/home/ammar/testing_nav_test_final_1.mp4'

DESKTOP_IMAGE_PATH = '/home/ammar/desktop_image.jpeg'



DIFFERENCE_LIMIT = 2e8








vidcap = cv2.VideoCapture(ORIGINAL_VIDEO)

desktop_image = cv2.imread(DESKTOP_IMAGE_PATH, cv2.IMREAD_UNCHANGED)
height, width, layers = desktop_image.shape
desktop_image_size = (width, height)

fourcc = cv2.VideoWriter_fourcc(*'DIVX')

success = True
count = 0
image_save_count = 0
video_save_count = 0

images_in_this_clip = []
out = None

should_start_record = True
should_record = True
while success:
	success,image = vidcap.read()
	cv2.imshow("Frame", image)
	k = cv2.waitKey(1) & 0xFF
	if k == ord('q'):
		break

	# Save image
	if k == ord('c'):
		fn = 'Frame_{}.jpeg'.format(image_save_count)
		cv2.imwrite(fn, image)
		print('Image saved: {}'.format(fn))
		image_save_count += 1

	difference_metric = np.sum(image - desktop_image)
	if difference_metric > DIFFERENCE_LIMIT:
		if out is None:
			video_file_name = 'Clip_{}.avi'.format(video_save_count)
			out = cv2.VideoWriter(video_file_name, fourcc, 60.0, desktop_image_size)
			video_save_count += 1

		out.write(image)
	else:
			if out:
				out.release()
				print('Saved video: {} with {} frames'.format(video_file_name, len(images_in_this_clip)))
			out = None
	# ipdb.set_trace()


	count += 1


if out:
	out.release()
vidcap.release()
cv2.destroyAllWindows()
