import socket
import pickle
import cv2
import threading
import time
import uuid
import os
import datetime

from easyocr import Reader


HEADERSIZE = 15
ITER_NUMBER = 4
LAST_TIME = 10


def remove_image(name):
    os.remove(f'/tmp/{name}.png')


def get_image(name):
    image = cv2.imread(f'/tmp/{name}.png')
    creation_date = int(os.path.getctime(f'/tmp/{name}.png'))
    remove_image(name)
    return image, creation_date


def thread_function():
    while not fin or len(images_list):
        time.sleep(0.01)
        lock.acquire()
        if images_list:
            image, creation_date = get_image(images_list.pop(0))
            lock.release()
            image_process(image, creation_date)
            continue
        lock.release()


def cleanup_text(text):
	return "".join([c if ord(c) < 128 else "" for c in text]).strip()


def bib_process(bib_number, image, creation_date):
    # Not pass
    if not bib_number in past_bibs:
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
            print(f'Send picture {bib_number} | creation date {datetime.datetime.fromtimestamp(creation_date)}')

            # Save image (temporary)
            unique_name = uuid.uuid4().hex
            cv2.imwrite(f'/tmp/{unique_name}.png', bibs_dict[bib_number]['image'])

            # Update data
            past_bibs.append(bib_number)
            bibs_dict.pop(bib_number)

    # Supp bib
    bibs_keys = list(bibs_dict.keys())
    for key in bibs_keys:
        if key != bib_number:
            bibs_dict[key]['last_time'] += 1
            if bibs_dict[key]['last_time'] >= LAST_TIME:
                bibs_dict.pop(key)


def image_process(orig_image, creation_date):
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
                bib_process(text, orig_image, creation_date)
                lock.release()


images_list = []
bibs_dict = {}
past_bibs = []
number_of_image = 0
fin = False

# Init thread
lock = threading.RLock()
thread = threading.Thread(target=thread_function)
thread.start()

# Init reader
reader = Reader(["fr"])

# Start socket
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(('',8100))
s.listen(10)

# Wait connection
conn,addr=s.accept()

# Calculate process time
start_time = time.time()

while True:
    # Receive image information
    picture_info = conn.recv(4096)

    # Information processing
    try:
        image_size = int(picture_info[:HEADERSIZE])
    except:
        fin = True
        break
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
    number_of_image += 1
    unique_name = uuid.uuid4().hex
    cv2.imwrite(f'/tmp/{unique_name}.png', orig_image)
    images_list.append(unique_name)
    lock.release()

# Wait end of process
thread.join()

# Calculate process time
end_time = time.time()
print(f'Process time: {end_time - start_time}s')
print(f'Number images processing: {number_of_image}')

# Close socket
conn.close()
s.close()
