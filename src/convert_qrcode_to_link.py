import cv2
from pyzbar import pyzbar
import re
import os


def get_link_qr_code(user_id):
    img = cv2.imread(f'src/img_{user_id}.png')
    data = pyzbar.decode(img)
    link = data[0].data.decode("utf-8")
    expression = r'(http?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})'
    regex = re.compile(expression, re.IGNORECASE)
    try:
        os.remove(f'src/img_{user_id}.png')
    except:
        pass
    if regex.match(link):
        return link
    else:
        return False
