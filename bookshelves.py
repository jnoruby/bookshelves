#!/usr/bin/env/python3

"""
• Analyse an image of a bookshelf containing books, segmenting it into images of
  the individual books' spines.
• Return OCR-generated text for each book spine, along with other identifying
  date (geometric, colour, etc.)
• Create database(s) of users' books.
"""

import ux  # Functions for terminal user interaction. TODO after tests -> app


def bookshelves():
    # Retrieve any arguments from command line (path to image, verbose setting).
    args = ux.get_args()

    # Set verbose boolean. Default to False if not set True in command line.
    v = args['verbose'] if args['verbose'] else False

    # Begin verbose reports if verbose set True.
    ux.print_program_introduction(args, v)

    # Get path to image and confirm that it's a valid image with imghdr.
    image_path, path_leaf = ux.get_image_path(args, v)


if __name__ == '__main__':
    bookshelves()
