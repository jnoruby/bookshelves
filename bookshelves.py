#!/usr/bin/env/python3

"""
• Analyse an image of a bookshelf containing books, segmenting it into images of
  the individual books' spines.
• Return OCR-generated text for each book spine, along with other identifying
  date (geometric, colour, etc.)
• Create database(s) of users' books.
"""

import ux  # Functions for terminal user interaction. TODO after tests -> app
import shelf_geometry as geom
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
                                   cv.THRESH_BINARY, 15, 0)
    window_name = 'Binary image'
    ux.image_report(bin_img, window_name, path_leaf, v)

    # Detect horizontal line segments to define shelves (-v and user confirms).
    axis_size = 20  # Determines structuring element size.
    window_name = 'Bookshelf identification image'
    ux.print_load_report(window_name, path_leaf, v)

    # TODO: Don't need axis here, but do for equiv. function getting book edges.
    # Get image of shelves against background, line segments.
    (shelf_bg_img,
     potential_shelves, __) = identify_shelves(bin_img, axis_size,
                                               window_name, v)

    # Calculate median angle of line segments to get inverse rotation angle.
    rotation_angle = -1 * geom.get_rotation_angle(potential_shelves, v)


def identify_shelves(image, axis, name, verbosity):
    # Get image of shelf line segments, line segments.
    shelf_img, potential_shelves = geom.detect_shelves(image, axis)
    try:
        bookshelf_count = len(potential_shelves)
    except TypeError:
        bookshelf_count = 0
    shelf_img = cv.addWeighted(image, 0.3, shelf_img, 0.7, 0.0)

    if verbosity:
        (shelf_img,
         potential_shelves, axis) = ux.user_shelf_check(image, shelf_img, name,
                                                        bookshelf_count)
    return shelf_img, potential_shelves, axis


if __name__ == '__main__':
    bookshelves()
