from easyocr import Reader
import cv2
from matplotlib import pyplot as plt


def cleanup_text(text):
	# strip out non-ASCII text so we can draw the text on the image
	# using OpenCV
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()

image = cv2.imread("coureur.jpg")

reader = Reader(["fr"])
results = reader.readtext(image)

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

plt.imshow(image)
plt.show()
cv2.waitKey(0)
cv2.destroyAllWindows()
