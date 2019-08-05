import os
import requests
import string

import cv2
import numpy as np

URL_TEMPLATE = 'https://www.papertraildesign.com/wp-content/uploads/2018/07/Scrabble-tile-{}-wood.jpg'


def download_letter_images(root_dir):
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    letter_img_dic = {}
    for c in string.ascii_uppercase:
        fpath = os.path.join(root_dir, 'scrabble-letter-{}.jpg'.format(c))
        if os.path.exists(fpath):
            print 'Letter "{}" already downloaded to "{}"'.format(c, fpath)
        else:
            print 'Downloading letter "{}" to "{}"'.format(c, fpath)
            url = URL_TEMPLATE.format(c)
            request = requests.get(url)
            open(fpath, 'wb').write(request.content)

        # Load image with OpenCV.
        img_arr = cv2.imread(fpath)
        letter_img_dic[c.lower()] = img_arr

    return letter_img_dic


def create_word_image(letter_img_dic, word, letter_px, gap_px):
    # Create the output image.
    width = len(word) * (letter_px + gap_px) + gap_px
    height = letter_px + 2 * gap_px
    # Use white as background.
    output_img = np.ones((height, width, 3)) * 255
    # Go through the letters one by one.
    for c_idx, c in enumerate(word):
        letter_img = letter_img_dic[c.lower()]
        # Resize the letter image to have the desired dimensions.
        resized_letter_img = cv2.resize(
            letter_img, (int(letter_px), int(letter_px)))
        #cv2.imshow('bla', resized_letter_img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        # Figure out where the letter's left top corner is in the output image.
        w_idx = gap_px + c_idx * (letter_px + gap_px)
        # Copy letter image to its place in the output image.
        output_img[gap_px:gap_px+letter_px, w_idx:w_idx+letter_px] = (
            resized_letter_img)

    return output_img


def main():
    letter_img_dic = download_letter_images('scrabble-letters')
    word = 'Neelam'
    word_image = create_word_image(
        letter_img_dic=letter_img_dic,
        word=word,
        letter_px=200,
        gap_px=10)
    cv2.imwrite('{}-scrabble-image.jpg'.format(word), word_image)


if __name__ == '__main__':
    main()
