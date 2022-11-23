"""A collection of tools used in other files in this module."""
import logging
import os
import pandas as pd

MAX_DATA_SIZE = 100 # Increase this later(?)

class CustomFormatter(logging.Formatter):
    cyan = "\x1b[36;1m"
    green = "\x1b[32;1m"
    yellow = "\x1b[33;1m"
    red = "\x1b[31;1m"
    magenta = "\x1b[35;1m"
    reset = "\x1b[0m"
    level = "[%(levelname)s]"
    format = "[%(asctime)s] %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: cyan + level + reset + format,
        logging.INFO: green + level + reset + format,
        logging.WARNING: yellow + level + reset + format,
        logging.ERROR: red + level + reset + format,
        logging.CRITICAL: magenta + level + reset + format
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def init_logger(logger=None, logLevel=None):
    logger = logger or logging.getLogger(__name__)
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)

    if logLevel:
        logger.setLevel(logging.getLevelName(logLevel))
        ch.setLevel(logging.getLevelName(logLevel))
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)

    return logger

def str_to_dict(string: str, delimiter: str='/') -> dict:
    """Given a string, separates each element of that string by a delimiter and converts to a dictionary.
       The last element in the dictionary will have a NONE key.
       Will handle NAME and DATA nodes.

    Args:
        string (str): A string

    Returns:
        dict: Dictionary representation of that string
    """
    # Split String by a deliminter
    separated = string.split(delimiter)
    # Does this string represent the root of a filesystem? (i.e starts with the delimiter?)
    is_root = separated[0] == ''
    # Remove empty elements from list
    separated = list(filter(None, separated))[1:]
    # Last element of the list should be None (Empty directory)
    last_item = { separated.pop() : '' }

    dict_repr = None
    if separated:
        for item in reversed(separated):
            dict_repr = {item: last_item}
            last_item = dict_repr
    else:
        dict_repr = last_item

    return dict_repr

def load_data(from_file: str='csv', num_partitions: int=1) -> dict:
    """Given a filename and a key to identify the file, will load and partition the data into a dictionary.

    Args:
        from_file (str, optional): Name of file to be loaded. Defaults to 'csv'.

    Returns:
        dict: Dictionary containing partitioned data
    """
    list_of_partitions = []
    partition_size = int(MAX_DATA_SIZE / num_partitions)
    filetype = from_file.split('.')[-1]
    if filetype == 'csv':
        assert os.path.exists(from_file), f"File {from_file} does not exist! Ensure you are giving the relative path to the file. HINT: Your current directory is {os.curdir}"            
        pdf = pd.read_csv(from_file)
        pdf.dropna(axis=1, inplace=True) # Drop NaN values (columnar)
        pdf.dropna(axis=0, inplace=True) # Drop NaN values (row)
        pdf.reset_index(drop=True, inplace=True) # Reset index after dropping NaNs
        pdf = pdf[:MAX_DATA_SIZE] # For spacial concerns, limit amount of data we use

        for i in range(0, MAX_DATA_SIZE - partition_size + 1, partition_size):
            partition = pdf.iloc[i:i+partition_size]
            list_of_partitions.append(partition)

        for i, df in enumerate(list_of_partitions):
            list_of_partitions[i] = df.to_dict(orient='index')
        
    else:
        raise NotImplementedError(f"Cannot load data from '{filetype}' files!")

    file_key = from_file.split('/')[-1]
    file_key = file_key.split('.')[:-1][0]
    dict_repr = {file_key: list_of_partitions}

    return dict_repr

def dict_to_file(data: dict, filetype: str) -> str:
    rebuilt_file = ""
    if filetype == "csv":
        # Should always get data that looks like {Number: {data...}, Number2: {data...}, ...}
        for idx in data.values():
            columns = list(idx.keys())
            columns = ','.join(columns)
            for datapoint in idx.values():
                rebuilt_file += str(datapoint) + ','
            rebuilt_file += '\n'
        rebuilt_file = columns + '\n' + rebuilt_file
    else:
        raise NotImplementedError(f"Filetype '.{filetype}' is not implemented")
    return rebuilt_file

# Keep this call to init logger
logger = init_logger(logLevel='DEBUG')
