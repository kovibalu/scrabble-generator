import os
import requests
import string

import cv2

URL_TEMPLATE = 'https://www.papertraildesign.com/wp-content/uploads/2018/07/Scrabble-tile-{}-wood.jpg'


def download_letter_images(root_dir):
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    letter_img_dic = {}
    for c in string.ascii_uppercase:
        url = URL_TEMPLATE.format(c)
        request = requests.get(url)
        fpath = os.path.join(root_dir, 'scrabble-letter-{}.jpg'.format(c))
        if os.path.exists(fpath):
            print 'Letter "{}" already downloaded to "{}"'.format(c, fpath)
        else:
            print 'Downloading letter "{}" to "{}"'.format(c, fpath)
            open(fpath, 'wb').write(request.content)

        # Load image with OpenCV.
        img_arr = cv2.imread(fpath)
        letter_img_dic[c.lower()] = img_arr

    return letter_img_dic


def main():
    letter_img_dic = download_letter_images('scrabble-letters')


if __name__ == '__main__':
    main()
