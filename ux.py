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

    def get_path_leaf(image_path):
        # Fix Windows file paths:
        image_path = image_path.replace('\\', '/')
        # Extract path leaf.
        path_leaf = image_path.split('/')[-1]
        return path_leaf

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
        if len(image_path) == 0:
            print('No image file was defined. Program cannot continue.')
            print('Exiting')
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
