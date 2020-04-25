import ux
import cv2 as cv
import numpy as np
from math import degrees, atan2


def detect_line_segments(img, axis_size):
    # Detect horizontal lines.
    line_img = create_line_structure(img, axis_size, 'horizontal')
    line_segments = cv.HoughLinesP(line_img, 1, np.pi/180, 15, 900, 500)

    return line_img, line_segments


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


def get_rotation_angle(line_segments, v):
    """
    Returns the average angle offset of line segments. Used to rotate an image
    based on shelf segments
    :param line_segments: a set of line segments delineating shelf edges
    :param v: whether to print verbose outfit
    :return: average angle offset
    """
    angles = np.empty([1, 1])
    try:
        for line_segment in line_segments:
            for x1, y1, x2, y2 in line_segment:
                angle = degrees(atan2(y2 - y1, x2 - x1))
                angles = np.append(angles, angle)
    except TypeError as e:
        print(e)
    rotation_angle = np.median(angles)
    ux.print_rotation_angle(rotation_angle, v)
    return rotation_angle


def get_shelf_y_values(line_segments, v):
    """
    :param line_segments: numpy array (segment count, 1, 4)
    :param v: whether to print verbose output.
    :return: an array of y values defining where bookshelves are in the image.
    """
    shelf_y = np.empty([0])
    shelf_ls = np.array(line_segments).flatten()[1:-1:2]
    shelf_ls = np.array(sorted(shelf_ls))
    shelf_ls = np.split(shelf_ls, np.where(np.diff(shelf_ls) > 100)[0] + 1)

    for shelf in shelf_ls:
        shelf_y = np.append(shelf_y, np.average(shelf))
    ux.print_shelf_y(shelf_y, v)
    return shelf_y


def split_shelf_regions(image, shelf_y, v):
    shelf_regions = []
    # Region is entire image if no shelves visible.
    if len(shelf_y) == 0:
        shelf_regions.append(image)

    else:
        # Define width range for slicing.
        w = range(0, image.shape[1])
        # Split from top to first shelf.
        count = 0
        try:
            h1 = int(shelf_y[count])
        except ValueError as e:
            print(e)
            h1 = None
            print('No regions. Exiting')
            exit()
        shelf_regions.append(image[0:h1, w])
        # Split from first shelf to nth shelf.
        while count < len(shelf_y) - 1:
            h2 = int(shelf_y[count + 1])
            shelf_regions.append(image[h1:h2, w])
            count = count + 1
        # Split from nth shelf to bottom.
        hn = int(shelf_y[count])
        shelf_regions.append(image[hn:image.shape[0], w])
    ux.print_shelf_region_report(shelf_regions, v)
    return shelf_regions


# From imutils, adapted.
def rotate_bound(image, angle):
    # Grab the dimensions of hte image and then determine the center.
    (h, w) = image.shape[:2]
    (cx, cy) = (w // 2, h // 2)
    # Grab the rotation matrix (applying the negative of the angle to
    # rotate clockwise), then grab the sine and cosine (i.e., the
    # rotation components of the matrix)
    m = cv.getRotationMatrix2D((cx, cy), -angle, 1.0)
    cos = np.abs(m[0, 0])
    sin = np.abs(m[0, 1])
    # Compute the new bounding dimensions of the image
    nw = int((h * sin) + (w * cos))
    nh = int((h * cos) + (w * sin))
    # Adjust the rotation matrix to take into account translation
    m[0, 2] += (nw / 2) - cx
    m[1, 2] += (nh / 2) - cy
    # Perform the actual rotation and return both the image and matrix.
    return cv.warpAffine(image, m, (nw, nh)), m


def get_slope(x1, y1, x2, y2):
    if x2 - x1 == 0:
        return None
    else:
        return (y2 - y1) / (x2 - x1)


def get_length(x1, y1, x2, y2):
    return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
