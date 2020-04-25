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
import imutils


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
    # Function returns image of shelves against background, line segments
    # defining shelves, and axis size.
    axis_size = 20  # Determines structuring element size.
    window_name = 'Bookshelf identification image'
    ux.print_load_report(window_name, path_leaf, v)
    (shelf_bg_img, shelf_img,
     potential_shelves, __) = identify_shelves(bin_img, axis_size,
                                               window_name, v)

    # Calculate median angle of line segments to get inverse rotation angle.
    rotation_angle = -1 * geom.get_rotation_angle(potential_shelves, v)

    # Rotate images that will be used for further processing, user output.
    # For user output:
    r_grey_img = imutils.rotate_bound(grey_img, rotation_angle)
    r_shelf_img = imutils.rotate_bound(shelf_img, rotation_angle)
    r_combo_img = cv.addWeighted(r_grey_img, 0.4, r_shelf_img, 0.6, 0.0)
    # For further processing:
    r_bin_img = imutils.rotate_bound(bin_img, rotation_angle)

    # User check rotation (-v)
    window_name = 'Rotated with respect to shelves image'

    ux.user_check(window_name, r_combo_img, False)

    # Get y value of peaks of distribution of y1 and y2 in bookshelves.
    # Split binary image into (shelf + 1) binary images for further processing.
    shelf_y = geom.get_shelf_y_values(potential_shelves, v)
    shelf_bin_imgs = geom.split_shelf_regions(r_bin_img, shelf_y, v)

    # Detect horizontal and vertical line segments to define book edges
    # (-v and user confirms). TODO Function returns ... (see above)
    axis_size = 180  # Determines structuring element size. # TODO vertical diff
    # TODO: Figure out a not image-specific way to exclude too-thin segment.
    # for shelf_bin_img in shelf_bin_imgs:
    #     identify_book_edges(shelf_bin_img, axis_size, v)
    identify_book_edges(shelf_bin_imgs[0], axis_size, v)


def identify_shelves(image, axis, name, v):
    # Get image of shelf line segments, line segments.
    shelf_img, potential_shelves = geom.detect_line_segments(image, axis)
    try:
        bookshelf_count = len(potential_shelves)
    except TypeError:
        bookshelf_count = 0
    shelf_bg_img = cv.addWeighted(image, 0.3, shelf_img, 0.7, 0.0)
    if v:
        (shelf_bg_img, shelf_img,
         potential_shelves, axis) = ux.user_shelf_check(image, shelf_bg_img,
                                                        name, bookshelf_count)

    return shelf_bg_img, shelf_img, potential_shelves, axis


def identify_book_edges(shelf_bin_img, axis_size, v):
    pass
    
    ux.user_check('Shelf binary image', shelf_bin_img, v)

    win_name = 'Horizontal edge checker'
    # Horizontal again with in shelf region)
    (__, shelf_bin_img_x, book_edges_x,
     axis_size) = ux.shelf_identification_report(shelf_bin_img, axis_size,
                                                 win_name, v)
    # Again with axis_size defined.
    (__, shelf_bin_img_x, book_edges_x,
     axis_size) = ux.shelf_identification_report(shelf_bin_img,
                                                 axis_size,
                                                 win_name, False)
    print(len(book_edges_x))
    win_name = 'Vertical edge checker'
    # Rotate image to detect verticals with same HoughLinesP settings.
    # rotate_bound is derived from imutils function but also returns matrix.
    r_shelf_bin_img, rotation_m = geom.rotate_bound(shelf_bin_img, 90)

    (__, r_shelf_bin_img_y, r_book_edges_y,
     axis_size) = ux.shelf_identification_report(r_shelf_bin_img,
                                                 axis_size,
                                                 win_name, v)
    # Again with axis size defined.
    (__, r_shelf_bin_img_y, r_book_edges_y,
     axis_size) = ux.shelf_identification_report(r_shelf_bin_img,
                                                 axis_size,
                                                 win_name, False)

    # Would be better to rotate points, but just combining the images instead
    # until can figure out affine transformation of point coords.
    shelf_bin_img_y, rotation_m = geom.rotate_bound(r_shelf_bin_img_y, -90)

    shelf_bin_img = cv.addWeighted(shelf_bin_img_x, 0.5, shelf_bin_img_y, 0.5,
                                   0.0)
    ux.user_check('combined', shelf_bin_img, v)
    ux.user_check('horizontal only', shelf_bin_img_x, True)


if __name__ == '__main__':
    bookshelves()
