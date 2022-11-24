from easyocr import Reader
import cv2
from matplotlib import pyplot as plt
import time


def cleanup_text(text):
	# strip out non-ASCII text so we can draw the text on the image
	# using OpenCV
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()

image = cv2.imread("data/coureur.jpg")

start = time.time()

reader = Reader(["fr"])

########## VERSION 1 ##########
# results = reader.readtext(image, canvas_size=360, text_threshold=0.4, link_threshold=0.4, low_text=0.4)

# for (bbox, text, prob) in results:
# 	(tl, tr, br, bl) = bbox
# 	tl = (int(tl[0]), int(tl[1]))
# 	tr = (int(tr[0]), int(tr[1]))
# 	br = (int(br[0]), int(br[1]))
# 	bl = (int(bl[0]), int(bl[1]))

# 	text = cleanup_text(text)

# 	cv2.rectangle(image, tl, br, (0, 255, 0), 2)
# 	cv2.putText(image, text, (tl[0], tl[1] - 10),
# 		cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)


########## VERSION 2 ##########
results, _ = reader.detect(image, canvas_size=360, text_threshold=0.4, link_threshold=0.4, low_text=0.4)

for rect in results[0]:
	x_min = rect[0]
	x_max = rect[1]
	y_min = rect[2]
	y_max = rect[3]

	cropped_image = image[y_min:y_max, x_min:x_max]

	text_data = reader.recognize(cropped_image)
	text_text = cleanup_text(text_data[0][1])

	cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
	cv2.putText(image, text_text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

end = time.time()

print(f'time : {end - start}')

plt.imshow(image)
plt.show()
