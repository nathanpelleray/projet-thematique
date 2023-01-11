import socket
import pickle
import cv2
import threading
import matplotlib.pyplot as plt
import time
import uuid
import os

from easyocr import Reader


HEADERSIZE = 15
ITER_NUMBER = 4
LAST_TIME = 10


def remove_image(name):
    os.remove(f'/tmp/{name}.png')


def get_image(name):
    image = cv2.imread(f'/tmp/{name}.png')
    remove_image(name)
    return image


def thread_function():
    while True:
        time.sleep(0.1)
        lock.acquire()
        if images_list:
            image = get_image(images_list.pop(0))
            lock.release()
            image_process(image)
            continue
        lock.release()


def cleanup_text(text):
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()


def bib_process(bib_number, image):
    # Create bib
    if bib_number not in bibs_dict:
        bibs_dict[bib_number] = {
            'iter_number': 1,
            'last_time': 0,
            'image': image
        }

    # Update bib data
    bibs_dict[bib_number]['iter_number'] += 1
    bibs_dict[bib_number]['last_time'] = 0

    # Send image
    if bibs_dict[bib_number]['iter_number'] >= ITER_NUMBER:
        bibs_dict[bib_number]['iter_number'] = 0
        print(f'Send picture {bib_number}')

    # Supp bib
    bibs_keys = list(bibs_dict.keys())
    for key in bibs_keys:
        if key != bib_number:
            bibs_dict[key]['last_time'] += 1
            if bibs_dict[key]['last_time'] >= LAST_TIME:
                bibs_dict.pop(key)


def image_process(orig_image):
    # Calculate ratio
    ratio = orig_image.shape[1] / 400

    # Cropped image
    for (xA, yA, xB, yB) in people_positions:
        (xA, yA, xB, yB) = (int(xA*ratio), int(yA*ratio), int(xB*ratio), int(yB*ratio))
        cropped_image = orig_image[yA:yB, xA:xB]
        
        results = reader.readtext(cropped_image, canvas_size=400, text_threshold=0.3, link_threshold=0.3, low_text=0.3)

        for (bbox, text, prob) in results:
            text = cleanup_text(text)

            if text.isdigit():
                lock.acquire()
                bib_process(text, orig_image)
                lock.release()


images_list = []
bibs_dict = {}

# Init thread
lock = threading.RLock()
threading.Thread(target=thread_function).start()

# Init reader
reader = Reader(["fr"])

# Start socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('127.0.0.1',8100))
s.listen(10)

# Wait connection
conn,addr=s.accept()

while True:
    # Receive image information
    picture_info = conn.recv(4096)

    # Information processing
    image_size = int(picture_info[:HEADERSIZE])
    people_positions = pickle.loads(picture_info[HEADERSIZE+1:])

    # Valide reception
    conn.send('OK'.encode('utf-8'))

    # Receive image
    data = b""
    while len(data) < image_size:
        data += conn.recv(4096)

    # Unserialize image
    frame = pickle.loads(data, fix_imports=True, encoding="bytes")
    orig_image = cv2.imdecode(frame, cv2.IMREAD_COLOR)

    lock.acquire()
    unique_name = uuid.uuid4().hex
    cv2.imwrite(f'/tmp/{unique_name}.png', orig_image)
    images_list.append(unique_name)
    lock.release()

# Close socket
s.close()