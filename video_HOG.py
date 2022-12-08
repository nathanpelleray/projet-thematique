import cv2
import time
import imutils
from imutils.object_detection import non_max_suppression
import numpy as np
from easyocr import Reader

import signal


exit = False

def signal_handler(signum, frame):  
    global exit
    exit = True

signal.signal(signal.SIGINT, signal_handler)


def cleanup_text(text):
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()


cam = cv2.VideoCapture('data/video_test.mp4')
if cam.isOpened() == False:
    print("Error")

hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

reader = Reader(["fr"])

out = cv2.VideoWriter('data/record.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (int(cam.get(3)),int(cam.get(4))))

previous_time = time.time()
while not exit:
    print(exit)
    current_time = time.time()
    dt = current_time - previous_time
    previous_time = current_time
    print(1/dt)

    ret, image = cam.read()
    ratio = image.shape[1] / 400
    orig_image = image.copy()
    image = imutils.resize(image, width=min(400, image.shape[1]))
    
    (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    for (xA, yA, xB, yB) in pick:
        # cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)

        (xA, yA, xB, yB) = (int(xA*ratio), int(yA*ratio), int(xB*ratio), int(yB*ratio))
        cropped_image = orig_image[yA:yB, xA:xB]
        print(cropped_image.shape)

        results = reader.readtext(cropped_image, canvas_size=400, text_threshold=0.3, link_threshold=0.3, low_text=0.3)

        for (bbox, text, prob) in results:
            if text.isdigit():
                (tl, tr, br, bl) = bbox
                tl = (int(tl[0] / ratio), int(tl[1] / ratio))
                tr = (int(tr[0]), int(tr[1]))
                br = (int(br[0] / ratio), int(br[1] / ratio))
                bl = (int(bl[0]), int(bl[1]))

                xA = int(xA / ratio) + int(tl[0] / ratio)
                yA = int(yA / ratio) + int(tl[1] / ratio)
                xB = int(xB / ratio) + int(br[0] / ratio)
                yB = int(yB / ratio) + int(br[1] / ratio)

                text = cleanup_text(text)
                print(f'#### {text} ####')

                cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
                cv2.putText(image, text, (xA, xA - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Reading the image in RGB to display it
    # color_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    out.write(image)

cam.release()
out.release()
