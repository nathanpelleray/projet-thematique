import cv2
import sys
import time
from easyocr import Reader
from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow)



class Thread(QThread):
    updateFrame = Signal(QImage)
    reader = None
    out = None

    def __init__(self, parent=None):
        super().__init__()
        self.reader = Reader(["fr"])

    def run(self):
        self.cam = cv2.VideoCapture(0)

        self.out = cv2.VideoWriter('data/record.avi',cv2.VideoWriter_fourcc('M','J','P','G'), 10, (int(self.cam.get(3)),int(self.cam.get(4))))

        previous_time = time.time()
        while True:
            current_time = time.time()
            dt = current_time - previous_time
            previous_time = current_time

            print(1/dt)

            ret, frame = self.cam.read()

            ########## VERSION 1 ##########
            results = self.reader.readtext(frame,  canvas_size=360, text_threshold=0.3, link_threshold=0.3, low_text=0.3)

            for (bbox, text, prob) in results:
                if text.isdigit():
                    (tl, tr, br, bl) = bbox
                    tl = (int(tl[0]), int(tl[1]))
                    tr = (int(tr[0]), int(tr[1]))
                    br = (int(br[0]), int(br[1]))
                    bl = (int(bl[0]), int(bl[1]))

                    text = self.cleanup_text(text)

                    cv2.rectangle(frame, tl, br, (0, 255, 0), 2)
                    cv2.putText(frame, text, (tl[0], tl[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            ########## VERSION 2 ##########
            # results, _ = self.reader.detect(frame, canvas_size=360, text_threshold=0.4, link_threshold=0.4, low_text=0.4)

            # for rect in results[0]:
            #     x_min = rect[0]
            #     x_max = rect[1]
            #     y_min = rect[2]
            #     y_max = rect[3]

            #     cropped_image = frame[y_min:y_max, x_min:x_max]

            #     text_data = self.reader.recognize(cropped_image)
            #     text_text = self.cleanup_text(text_data[0][1])

            #     cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            #     cv2.putText(frame, text_text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Reading the image in RGB to display it
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            self.out.write(frame)

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
