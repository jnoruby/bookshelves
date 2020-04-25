import shelf_geometry as geom
import argparse
import imghdr
import cv2 as cv


class ClickGetter:
    good = False
    done = False

    def callback(self, event, x, y, flags, params):
        if self.done:
            return
        elif event == cv.EVENT_LBUTTONDOWN:
            self.good = True
            self.done = True
        return x, y, flags, params


def get_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', '--image', type=str,
                            help='path to input image')
    arg_parser.add_argument('-v', '--verbose', dest='verbose', default=False,
                            action='store_true', help='whether terminal '
                                                      'interface is verbose')
    args = vars(arg_parser.parse_args())
    return args


def print_program_introduction(args, v):
    msg = (f'This program reads an image of a bookshelf containing books, '
           f'segments it into images of the individual books\' spines, returns '
           f'OCR-generated text for each book spine, and creates a first draft'
           f' book inventory.')
    if v:
        print(msg)
        print(f'Command-line arguments: {args}')


def get_image_path(args, v):

    def get_path_leaf(path):
        # Fix Windows file paths:
        leaf = path.replace('\\', '/')
        # Extract path leaf.
        leaf = leaf.split('/')[-1]
        return leaf

    if args['image'] is not None:
        image_path = args['image']
        argument_source = 'command-line argument'
    else:
        image_path = input(f'Please enter path to bookshelf image.\n Supported '
                           f'file formats are defined by imghdr '
                           f'{get_imghdr_supported_file_formats()}.\n'
                           f'Path: ')
        argument_source = 'runtime user input'
    path_leaf = get_path_leaf(image_path)
    if v:
        valid_formats = get_imghdr_supported_file_formats().split(' ')
        valid_formats.append('jpg')
        file_format = path_leaf.split('.')[-1]
        if len(image_path) == 0:
            print('No image file was defined.')
            print('Program cannot continue. Exiting')
            exit()
        if file_format not in valid_formats:
            print(f'.{file_format} files are not supported.')
            print('Program cannot continue. Exiting')
            exit()
        print(f'Testing path to bookshelf image {path_leaf}, defined by '
              f'{argument_source}')
    return image_path, path_leaf


def get_imghdr_supported_file_formats():
    """
    Retrieves list of file formats that can be verified by imghdr, from the
    module's own list of functions (if the variable name is unchanged), or from
    a local string (accurate as of 2020-04-24) if the variable name changes.
    :return: file formats verifiable by imghdr, space separated
    """
    supported_types = ''
    try:
        for test in imghdr.tests:
            supported_types += test.__name__[5:]  # Ignoring prefix 'test_'
            supported_types += ' '
    except AttributeError:
        supported_types = ('jpeg png gif tiff rgb bpm pgm ppm rast xbm bmp '
                           'webp exr')
    return supported_types.strip()


def open_file(path, leaf, v):
    try:
        fd = open(path, 'r')
        if v:
            print(f'Loading {leaf}...')
        # Check validity of file with imghdr, as OpenCV has no error checking.
        if imghdr.what(path) is not None:
            fd.close()
            return path
        else:
            print(f'{leaf} is not recognised as a valid image by imghdr.')
            fd.close()
            exit()
    except IOError as e:
        print(e)
        exit()


def image_report(img, name, leaf, v):
    if v:
        print_load_report(name, leaf, v)
        user_check(name, img, v)


def print_load_report(name, leaf, v):
    image_type = ' '.join(name.split(' ')[0:-1]).lower()
    if image_type != 'original' and v:
        print(f'{leaf} converted to {image_type}.')


def user_check(name, img, v):
    if v:
        print('Click the image and press ESC to confirm image.')
        print('Press ESC without clicking to reject image.')
        ok = image_ok(name, img)
        if not ok:
            print(f'{name} not confirmed by user. Exiting.')
            exit()


def image_ok(name, img):
    create_window(name, img)
    click_getter = ClickGetter()
    cv.setMouseCallback(name, click_getter.callback)
    while not click_getter.done:
        cv.imshow(name, img)
        if cv.waitKey(0) == 27:
            return click_getter.good
    cv.moveWindow(name, 500, 0)
    cv.waitKey(0)
    return click_getter.good


def create_window(name, img):
    window_width, window_height = resize_window(img)
    cv.namedWindow(name, cv.WINDOW_NORMAL)
    cv.resizeWindow(name, window_width, window_height)
    cv.moveWindow(name, 50, 50)


def resize_window(img):
    # Locals, change for other testing screens. UI will not use this.
    screen_res = 2560, 1440
    scale_width = screen_res[0] / img.shape[1]
    scale_height = screen_res[1] / img.shape[0]
    scale = min(scale_width, scale_height)
    window_width = int(img.shape[1] * scale / 2)
    window_height = int(img.shape[0] * scale / 2)
    return window_width, window_height


def user_shelf_check(image, shelf_bg_img, win_name, bookshelf_count):
    def nothing(x):
        return x

    print(f'{bookshelf_count} potential bookshelf line segments extracted.')
    print('Increase axis size slider if not enough shelves found.')
    print('Decrease axis size slide if too many shelves found.')

    potential_shelves = None
    shelf_img = None
    axis = None
    window_width, window_height = resize_window(shelf_bg_img)
    cv.namedWindow(win_name, cv.WINDOW_NORMAL)
    cv.resizeWindow(win_name, window_width, window_height)
    cv.moveWindow(win_name, 20, 20)
    cv.createTrackbar('Axis size', win_name, 15, 300, nothing)

    while True:
        cv.imshow(win_name, shelf_bg_img)
        k = cv.waitKey(1) & 0xFF
        if k == 27:
            break

        axis = cv.getTrackbarPos('Axis size', win_name)
        shelf_img, potential_shelves = geom.detect_line_segments(image, axis)
        shelf_bg_img = cv.addWeighted(image, 0.3, shelf_img,
                                      0.7, 0.0)

    return shelf_bg_img, shelf_img, potential_shelves, axis


def print_rotation_angle(rotation_angle, v):
    if v:
        print(f'Bookshelves are offset {rotation_angle}° from horizontal.')
        print(f'Images will be rotated {-1 * rotation_angle}°.')


def print_shelf_y(shelf_y, v):
    if v:
        print(f'Shelves located at {shelf_y}')


def print_shelf_region_report(shelf_regions, v):
    if v:
        print(f'Image split into {len(shelf_regions)} regions.')


def shelf_identification_report(binary_img, axis_size, name, v):

    horizontal_image, shelves = geom.detect_line_segments(binary_img,
                                                          axis_size)
    try:
        bookshelf_count = len(shelves)
    except TypeError:
        bookshelf_count = 0
    if v:
        print(f'{bookshelf_count} potential bookshelf line segments extracted.')
        print('Increase axis size slider if not enough shelves found.')
        print('Decrease axis size slide if too many shelves found.')
    shelf_img = cv.addWeighted(binary_img, 0.3, horizontal_image, 0.7, 0.0)

    if v:
        def nothing(x):
            return x
        window_name = name
        window_width, window_height = resize_window(shelf_img)
        cv.namedWindow(window_name, cv.WINDOW_NORMAL)
        cv.resizeWindow(window_name, window_width, window_height)
        cv.moveWindow(window_name, 20, 20)
        cv.createTrackbar('Axis size', window_name, 15, 300, nothing)

        while True:
            cv.imshow(window_name, shelf_img)
            k = cv.waitKey(1) & 0xFF
            if k == 27:
                break

            axis_size = cv.getTrackbarPos('Axis size', window_name)
            horizontal_img, shelves = geom.detect_line_segments(binary_img,
                                                                axis_size)
            shelf_img = cv.addWeighted(binary_img, 0.3, horizontal_img,
                                       0.7, 0.0)

        cv.destroyAllWindows()
    return shelf_img, horizontal_image, shelves, axis_size
