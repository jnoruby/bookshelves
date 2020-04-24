#!/usr/bin/env/python3

"""
• Analyse an image of a bookshelf containing books, segmenting it into images of
  the individual books' spines.
• Return OCR-generated text for each book spine, along with other identifying
  date (geometric, colour, etc.)
• Create database(s) of users' books.
"""

import ux  # Functions for terminal user interaction. TODO after tests -> app
import cv2 as cv  # OpenCV for image processing.


def bookshelves():
    # Retrieve any arguments from command line (path to image, verbose setting).
    args = ux.get_args()

    # Set verbose boolean. Default to False if not set True in command line.
    v = args['verbose'] if args['verbose'] else False

    # Begin verbose reports if verbose set True.
    ux.print_program_introduction(args, v)

    # Get path to image, rejecting paths not supported by imghdr.
    image_path, path_leaf = ux.get_image_path(args, v)
    image_path = ux.open_file(image_path, path_leaf, v)

    # Read original (probably colour) image (-v and user confirms).
    # TODO: All current image processing works on greyscale, but colour image
    # TODO will be needed for later spine analysis.
    img = cv.imread(image_path)
    window_name = 'Original image'
    ux.image_report(img, window_name, path_leaf, v)

    # Convert image to greyscale (-v and user confirms).
    grey_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    window_name = 'Greyscale image'
    ux.image_report(grey_img, window_name, path_leaf, v)

    # Convert image to binary (-v and user confirms).
    # TODO: Check if parameters to adaptiveThreshold affect final lines.
    bin_img = cv.bitwise_not(grey_img)
    bin_img = cv.adaptiveThreshold(bin_img, 255, cv.ADAPTIVE_THRESH_MEAN_C,
                                   cv.THRESH_BINARY, 81, 0)
    window_name = 'Binary image'
    ux.image_report(bin_img, window_name, path_leaf, v)


if __name__ == '__main__':
    bookshelves()
