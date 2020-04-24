import cv2 as cv
import numpy as np


def detect_shelves(img, axis_size):
    # Detect horizontal lines.
    line_structure = create_line_structure(img, axis_size, 'horizontal')
    potential_bookshelves = cv.HoughLinesP(line_structure, 1, np.pi/180, 15,
                                           900, 500)
    return line_structure, potential_bookshelves


def create_line_structure(image, axis_size, direction):
    if direction == 'vertical':
        dimension = 0
    elif direction == 'horizontal':
        dimension = 1
    else:
        dimension = -1
        print('Image structure cannot be created. Impossible dimension type '
              'specified.')
        exit()

    # Create the image that we will use to extract lines.
    line_image = np.copy(image)

    # Specify size of axis.
    pixels = line_image.shape[dimension]

    # Calculate dimension size. Return if no lines found (dimension_size = 0)
    try:
        dimension_size = pixels // axis_size
    except ZeroDivisionError:
        dimension_size = 0
        print('No bookshelves found. Structuring element cannot be calculated.')
    if dimension_size == 0:
        return line_image

    # Create structure elements to extract lines through morphology operations.
    if direction == 'vertical':
        line_structure = cv.getStructuringElement(cv.MORPH_RECT,
                                                  (1, dimension_size))
    else:
        line_structure = cv.getStructuringElement(cv.MORPH_RECT,
                                                  (dimension_size, 1))
    # Apply morphology operations.
    line_image = cv.erode(line_image, line_structure)
    line_image = cv.dilate(line_image, line_structure)

    return line_image
