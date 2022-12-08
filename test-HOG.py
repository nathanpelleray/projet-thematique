import cv2
import sys
import time
from easyocr import Reader
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow)
import pytesseract
import numpy as np
import imutils
from imutils.object_detection import non_max_suppression
from matplotlib import pyplot as plt


class Thread(QThread):
    updateFrame = Signal(QImage)
    reader = None
    out = None

    def __init__(self, parent=None):
        super().__init__()
        self.reader = Reader(["fr"])

    def run(self):
        self.cam = cv2.VideoCapture('data/video_test.mp4')

        if self.cam.isOpened() == False:
            print("Error")

        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())


        self.out = cv2.VideoWriter('data/record.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (int(self.cam.get(3)),int(self.cam.get(4))))

        previous_time = time.time()
        while True:
            current_time = time.time()
            dt = current_time - previous_time
            previous_time = current_time

            print(1/dt)

            ret, image = self.cam.read()
            ratio = image.shape[1] / 400
            orig_image = image.copy()
            image = imutils.resize(image, width=min(400, image.shape[1]))
            

            # detect people in the image
            (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)

            # apply non-maxima suppression to the bounding boxes using a
            # fairly large overlap threshold to try to maintain overlapping
            # boxes that are still people
            rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
            pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

            # draw the final bounding boxes
            for (xA, yA, xB, yB) in pick:
                # cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)

                (xA, yA, xB, yB) = (int(xA*ratio), int(yA*ratio), int(xB*ratio), int(yB*ratio))
                cropped_image = orig_image[yA:yB, xA:xB]
                print(cropped_image.shape)

                results = self.reader.readtext(cropped_image, canvas_size=400, text_threshold=0.3, link_threshold=0.3, low_text=0.3)

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

                        text = self.cleanup_text(text)
                        print(f'#### {text} ####')

                        cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
                        cv2.putText(image, text, (xA, xA - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)


            # ret, frame = self.cam.read()
            # print(frame.shape)
            # # frame = cv2.resize(frame, (frame.shape[0] // 2, frame.shape[1] // 2))
            # # using a greyscale picture, also for faster detection
            # gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            # # detect people in the image
            # # returns the bounding boxes for the detected objects
            # # boxes, weights = hog.detectMultiScale(frame, winStride=(8,8) )
            # boxes, weights = hog.detectMultiScale(gray, winStride=(4, 4), padding=(8, 8), scale=1.05)

            # boxes = np.array([[x, y, x + w, y + h] for (x, y, w, h) in boxes])

            # for (xA, yA, xB, yB) in boxes:
            #     # display the detected boxes in the colour picture
            #     cv2.rectangle(frame, (xA, yA), (xB, yB),
            #                     (0, 255, 0), 2)



            # Reading the image in RGB to display it
            color_frame = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            self.out.write(image)

            # Creating and scaling QImage
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)

            self.updateFrame.emit(img)

    def cleanup_text(self, text):
	    return "".join([c if ord(c) < 128 else "" for c in text]).strip()



class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 640, 480)

        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)

        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updateFrame.connect(self.setImage)
        self.th.start()

    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

app = QApplication()
w = Window()
w.show()
sys.exit(app.exec())
