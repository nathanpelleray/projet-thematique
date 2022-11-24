import cv2
import pytesseract
from matplotlib import pyplot as plt

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

image = cv2.imread('dossard.jpg')
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
# threshold_img = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
# threshold_img = cv2.adaptiveThreshold(gray_image, 0, 255, cv2.THRESH_BINARY | cv2.ADAPTIVE_THRESH_GAUSSIAN_C)[1]

custom_config = r'--oem 3 --psm 6'
details = pytesseract.image_to_data(threshold_img, output_type=pytesseract.Output.DICT, config=custom_config, lang='eng')

total_boxes = len(details['text'])

for sequence_number in range(total_boxes):
    if int(details['conf'][sequence_number]) >30:
        (x, y, w, h) = (details['left'][sequence_number], details['top'][sequence_number], details['width'][sequence_number],  details['height'][sequence_number])
        threshold_img = cv2.rectangle(threshold_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

parse_text = []
word_list = []
last_word = ''

for word in details['text']:
    if word != '':
        word_list.append(word)
    
    if (last_word != '' and word == '') or (word == details['text'][-1]):
        parse_text.append(word_list)
        word_list = []

# print(parse_text)

print(pytesseract.image_to_string(image))

plt.imshow(threshold_img)
plt.show()
cv2.waitKey(0)
cv2.destroyAllWindows()
