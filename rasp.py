import imutils
import cv2
import socket
import pickle
import numpy as np
import time

from imutils.object_detection import non_max_suppression


HEADERSIZE = 15


# Init hog detection
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

# Start socket 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8100))

# Init camera
cam = cv2.VideoCapture('data/video_test.mp4')
if cam.isOpened() == False:
    print("Error")

previous_time = time.time()
while True:
    current_time = time.time()
    dt = current_time - previous_time
    previous_time = current_time

    print(1/dt)

    # Image
    ret, image = cam.read()
    ratio = image.shape[1] / 400
    orig_image = image.copy()

    # Resize image
    image = imutils.resize(image, width=min(400, image.shape[1]))

    # Person detection
    (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4), padding=(8, 8), scale=1.05)
    rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
    pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

    people_positions = []
    for (xA, yA, xB, yB) in pick:
        people_positions.append((int(xA), int(yA), int(xB), int(yB)))

    if people_positions:
        # Encode and serialize image
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, frame = cv2.imencode('.jpg', orig_image, encode_param)
        data = pickle.dumps(frame, 0)

        # Send image information
        size = len(data)
        people_positions_data = pickle.dumps(people_positions)
        msg = bytes(f"{size:<{HEADERSIZE}};", 'utf-8')+people_positions_data
        client_socket.send(msg)

        # Check reception
        response = client_socket.recv(255).decode('utf-8')
        if response == 'OK':
            # Send image
            client_socket.sendall(data)

# Close socket
client_socket.close()