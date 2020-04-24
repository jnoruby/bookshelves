import argparse


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
