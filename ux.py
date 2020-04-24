import argparse
import imghdr


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
