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
results = reader.readtext(image, canvas_size=360, text_threshold=0.4, link_threshold=0.4, low_text=0.4)

for (bbox, text, prob) in results:
	(tl, tr, br, bl) = bbox
	tl = (int(tl[0]), int(tl[1]))
	tr = (int(tr[0]), int(tr[1]))
	br = (int(br[0]), int(br[1]))
	bl = (int(bl[0]), int(bl[1]))

	text = cleanup_text(text)

	cv2.rectangle(image, tl, br, (0, 255, 0), 2)
	cv2.putText(image, text, (tl[0], tl[1] - 10),
		cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

end = time.time()

print(f'time : {end - start}')

plt.imshow(image)
plt.show()
