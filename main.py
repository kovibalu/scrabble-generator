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
    output_width = len(word) * (letter_px + gap_px) + gap_px
    output_height = letter_px + 2 * gap_px
    # Use white as background.
    output_img = np.ones((output_height, output_width, 3)) * 255
    # Go through the letters one by one.
    for c_idx, c in enumerate(word):
        # Handle space as a special case. Here we don't need to draw anything.
        if c == ' ':
            continue

        letter_img = letter_img_dic[c.lower()]
        # Resize the letter image to have the desired dimensions.
        resized_letter_img = cv2.resize(
            letter_img, (int(letter_px), int(letter_px)))
        # Figure out where the letter's left top corner is in the output image.
        w_idx = gap_px + c_idx * (letter_px + gap_px)
        # Copy letter image to its place in the output image.
        output_img[gap_px:gap_px+letter_px, w_idx:w_idx+letter_px] = (
            resized_letter_img)

    return output_img


def create_words_image(letter_img_dic,
                       words,
                       letter_px,
                       gap_px,
                       max_letters_per_row):
    # Create the image row-by-row.
    row_images = []
    cum_letters_per_row = 0
    cum_words = []
    for word in words:
        # Handle the first word as a special case.
        if cum_words:
            new_cum_letters_per_row = cum_letters_per_row + len(word) + 1
        else:
            new_cum_letters_per_row = len(word)

        if new_cum_letters_per_row > max_letters_per_row:
            # Render row if we went over the max letter limit for the current
            # row.
            if cum_words:
                row_image = create_word_image(
                    letter_img_dic=letter_img_dic,
                    word=' '.join(cum_words),
                    letter_px=letter_px,
                    gap_px=gap_px)
                row_images.append(row_image)
            # Reset cumulative counters to start a new row.
            cum_letters_per_row = len(word)
            cum_words = [word]
        else:
            cum_letters_per_row = new_cum_letters_per_row
            cum_words.append(word)

    # Render last row if needed.
    if cum_words:
        row_image = create_word_image(
            letter_img_dic=letter_img_dic,
            word=' '.join(cum_words),
            letter_px=letter_px,
            gap_px=gap_px)
        row_images.append(row_image)

    # Create the output image and copy each row in.
    # Get the max width between all rows.
    output_width = max([ri.shape[1] for ri in row_images])
    # Get the sum of the height of all rows.
    output_height = sum([ri.shape[0] for ri in row_images])
    # Use white as background.
    output_img = np.ones((output_height, output_width, 3)) * 255

    cum_height = 0
    for ri in row_images:
        ri_height, ri_width, _ = ri.shape
        # Center each row.
        from_width = (output_width - ri_width) // 2
        output_img[cum_height:cum_height+ri_height,
                   from_width:from_width+ri_width] = ri
        cum_height += ri_height

    return output_img


def main():
    letter_img_dic = download_letter_images('scrabble-letters')
    word_image = create_words_image(
        letter_img_dic=letter_img_dic,
        words=['Neelam', 'loves', 'Balazs'],
        letter_px=200,
        gap_px=10,
        max_letters_per_row=12)
    cv2.imwrite('cool-scrabble-image.jpg', word_image)


if __name__ == '__main__':
    main()
