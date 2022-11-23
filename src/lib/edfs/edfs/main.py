# Placeholder for main.py
import argparse
from edfs.tools import logger
from edfs.commands import mkdir, ls, cat, rm, put
# from sql import run


def entrypoint():
    """Entrypoint."""
    parser = argparse.ArgumentParser(description='EDFS')
    parser.add_argument('database', help='Database implementation for EDFS (either MySQL or Firebase)', choices=('mysql', 'firebase'))

    hdfs_commands = parser.add_mutually_exclusive_group()
    hdfs_commands.add_argument('-mkdir', help='Accepts a directory path as an argument, creates a directory at the given location.')
    hdfs_commands.add_argument('-ls', help='Accepts a directory path as an argument, lists files at path given.')
    hdfs_commands.add_argument('-cat', help='Accepts filepath as an argument, displays information about the file.')
    hdfs_commands.add_argument('-rm', help='Accepts filepath as an argument, removes file from hdfs.')
    hdfs_commands.add_argument('-put', help='Accepts filepath, database location, and number of partitions as an argument', nargs=3)

    args = vars(parser.parse_args())
    logger.debug(args)

    if args['database'] == 'mysql':
        run()

    if args['mkdir']:
        mkdir(filepath=args['mkdir'], database=args['database'])

    elif args['ls']:
        ls(filepath=args['ls'], database=args['database'])

    elif args['cat']:
        cat(filename=args['cat'], database=args['database'])

    elif args['rm']:
        rm(filename=args['rm'], database=args['database'])

    elif args['put']:
        put_args = args['put']
        filename = put_args[0]
        location_in_database = put_args[1]
        number_partitions = int(put_args[2])
        put(filename=filename, location=location_in_database, k=number_partitions, database=args['database'])

    else:
        pass
        #raise NotImplementedError


if __name__ == "__main__":
    entrypoint()
