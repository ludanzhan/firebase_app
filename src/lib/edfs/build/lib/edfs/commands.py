# Placeholder for commands.py, a file that will contain definitions for commands used by edfs
from edfs.tools import *

import pandas as pd
import json
from uuid import uuid4
from functools import reduce
import firebase_admin
from firebase_admin import db
import os
import re
# For more information on the firebase api, please check out https://firebase.google.com/docs/reference/admin/python/firebase_admin.db

curdir = os.path.dirname(os.path.abspath(__file__))
# NOTE: In general, never store credentials or other important information in plaintext.
#       Only doing this for this project
credential_filename = 'dsci-551-project-177ec-firebase-adminsdk-q5gxp-70d290b8aa.json'
database_url = 'https://dsci-551-project-177ec-default-rtdb.firebaseio.com/'

firebase_credentials = os.path.relpath(os.path.join(curdir, '..', '..', '..', '..', 'secrets', credential_filename))

if not os.path.exists(firebase_credentials):
    raise FileNotFoundError(f"{credential_filename} not in expected location. Checked {firebase_credentials}")
else:
    firebase_credentials = os.path.abspath(firebase_credentials)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = firebase_credentials

cred_obj = firebase_admin.credentials.Certificate(firebase_credentials)

default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL': database_url
    })

def firebase_connect(initial_path: str='/'):
    """Connects to firebase databaes

    Args:
        initial_path (str, optional): Node of the firebase database to use as reference root.. Defaults to '/'.

    Returns:
        firebase_admin.db.Reference: Reference to node at initial path
    """
    if initial_path.find('.') != -1:
        initial_path = initial_path.split('.')[0]

    return db.reference(initial_path)

def check_if_exists(path: str='/') -> bool:
    """Checks if a given file exists in a firebase database

    Args:
        path (str, optional): path of file. Defaults to '/'.

    Returns:
        bool: If file exists.
    """
    is_file = path.find('.') != -1
    if is_file:
        path = path.split('.')[0]
    if not path.startswith('/'):
        path = '/' + path
    ref = db.reference('name' + path) # Only checking name node, if we did things right, data node should be guaranteed to exist.        
    data = ref.get()
    exists = data is not None # Something is a file if the child of the value of the child is a path
    return exists, data, is_file
def mkdir(filepath: str, database: str='firebase') -> str:
    """Connects to chosen database and creates proper file structure by writing a json object (firebase) or a mysql database.

    Args:
        filepath (str): Logical path to file in database from root.
        database (str, optional): Database implementation to use for this command. Defaults to 'firebase'.
    
    Return:
        str: Representation of the object that was written.
    """
    # When Making a directory, need to find highest level directory that _does not_ exist, then use the one above that as a ref
    # If nothing exists, use '/' (root)
    # For example, if our mkdir command wants "user/people/john" and our database just has user, we want the reference to be from user and to create /people/john
    # Then GET the data located at user/, ADD what we want, then SET
    fp = filepath
    to_be_written = ''
    if database == 'firebase':
        exists, data, _ = check_if_exists(fp)
        while not exists:
            fp = fp.split('/')
            to_be_written = '/' + fp[-1] + to_be_written
            fp = '/'.join(fp[:-1])
            exists, data, _ = check_if_exists(fp)

        if to_be_written:
            name_ref = firebase_connect('name/' + fp)
            name_ref.update(data)

    else:
        raise NotImplementedError("SQL has not been implemented for this function")
    
    if not to_be_written:
        logger.warning(f"Directory {filepath} already exists!")
        filepath = ''
    else:
        logger.debug(f"Created {filepath}")
    
    return filepath


def ls(filepath: str, database: str='firebase') -> str:
    """Connects to the chosen database and returns the contents of the database at the location given by 'filepath'.

    Args:
        filepath (str): Logical path to file in database from root.
        database (str, optional): Database implementation to use for this command. Defaults to 'firebase'.

    Return:
        str: Object located at the filepath, if it exists.
    """
    if database == 'firebase':
        exists, data, _ = check_if_exists(filepath)
        if exists:
            files = list(data.keys())
            str_repr = '\t'.join(files)
            print(str_repr)
            return files
    else:
        raise NotImplementedError("SQL has not been implemented for this function")


def cat(filename: str, database: str='firebase') -> str:
    """Connects to a database and gets the contents of a single file at that location.

    Args:
        filename (str): Logical path to file in database from root.
        database (str, optional): Database implementation to use for this command. Defaults to 'firebase'.

    Return:
        str: Contents of the file located at the filepath, if it exists.
    """
    reconstructed_file = ""
    if database == 'firebase':
        exists, _, is_file = check_if_exists(filename)
        if exists and is_file:
            locations = getPartitionLocations(filename)
            running_total = []
            for partition_number, partition in enumerate(locations):
                running_total.append(readPartition(partition, partition_number, database="firebase")) # list of dicts

            joined = reduce(lambda a, b: {**a, **b}, running_total)
            reconstructed_file = dict_to_file(joined, filename.split('.')[-1])
        elif exists and not is_file:
            logger.error(f"Cannot 'cat' a directory!")
        else:
            logger.error(f"File '{filename}' does not exist!")

    else:
        raise NotImplementedError("SQL has not been implemented for this function")

    return reconstructed_file

def rm(filename: str, database: str='firebase') -> bool:
    """Connects to the chosen database and DELETS the file located at the given string, without modifying the directories above the file.

    Args:
        filename (str): Logical path to file in database from root.
        database (str, optional): Database implementation to use for this command. Defaults to 'firebase'.

    Return:
        bool: Whether or not the operation was successful.
    """
    operation_successful = False
    if database == 'firebase':
        exists, _, is_file = check_if_exists(filename)
        if exists and is_file:
            name_ref = firebase_connect('name/' + filename).parent # Get all keys, then remove those files
            data_ref = firebase_connect('data/')

            key = filename.split('/')[-1]
            if is_file:
                key = key.split('.')[0]
            name_data = name_ref.get()
            data_partitions = data_ref.get()
            for partition in name_data[key]:
                data_partitions.pop(partition.split('/')[-1])
            name_data.pop(key)
            name_ref.set(name_data)
            data_ref.set(data_partitions)

            # Handle accidentally removing database.
            ref = firebase_connect()
            if not ref.get():
                ref.set({"name": "", "data": ""})

            operation_successful = True

        else:
            logger.error(f"File '{filename}' does not exist!")
    else:
        raise NotImplementedError("SQL has not been implemented for this function")

    return operation_successful


def put(filename: str, location: str, k: int, database: str='firebase') -> bool:
    """Calls the partition() function and uses the output to write a json object to the database at the location specified.

    Args:
        filename (str): Logical path to file in database from root.
        location (str): Location to write specific partition of file.
        k (int): Number of partitions that the file should be divided into.
        database (str, optional): Database implementation to use for this command. Defaults to 'firebase'.
    
    Returns:
        bool: Whether the operation was successful.
    """
    k = int(k)
    operation_successful = False
    name_nodes, data_nodes = partition(filename, k, database, location)

    if database == 'firebase':
        exists, _, _ = check_if_exists(location)
        if exists:
            name_ref = firebase_connect('name/' + location)
            data_ref = firebase_connect('data/')
            name_ref.update(name_nodes)
            data_ref.update(data_nodes)
            operation_successful = True
        else:
            logger.error(f"File '{location}' does not exist!")
    else:
        raise NotImplementedError("SQL has not been implemented for this function")
    
    return operation_successful

def partition(filename: str, k: int, database: str='firebase', location: str='') -> tuple:
    """Load the contents of filename as a json (or SQL) object, divide the object into k partitions, and smartly write the k partitions into separate locations in the selected database.
    NOTE: Data is loaded into a dictionary, then that dictionary is divided into two, one with data (stored in partitions) and one with partition locations.

    Args:
        filename (str): Logical path to file in database from root.
        k (int): Number of partitions that the file should be divided into.
        database (str, optional): Database implementation to use for this command. Defaults to 'firebase'.

    Returns:
        tuple: Data that will be stored in the name node and data node
    """
    assert location, f"Partition needs the location information that is given from `put`"

    if not location.endswith('/'):
        location += '/'
        
    data = load_data(from_file=filename, num_partitions=k)
    file_key = filename.split('/')[-1]
    file_key = file_key.split('.')[:-1][0]
    data = data[file_key]
    full_name_node_dict = {file_key : ""}
    full_data_node_dict = {}
    name_node_dict = {}
    data_node_dict = {}

    for partition_num, partition in enumerate(data):
        hash_key = uuid4().hex
        name_node_dict[partition_num] = name_node_dict.get(partition_num, '')
        data_node_dict[hash_key] = data_node_dict.get(hash_key, '')
        name_node_dict[partition_num] = f"/data/{hash_key}" # String that points to the partition in data_node
        data_node_dict[hash_key] = partition


    full_name_node_dict[file_key] = name_node_dict
    full_data_node_dict = data_node_dict

    return full_name_node_dict, full_data_node_dict


def getPartitionLocations(filepath: str, database: str='firebase') -> str:
    """Gets list of file partitions stored at filepath

    Args:
        filepath (str): Logical path to file in database from root.
        database (str, optional): Database implementation to use for this command. Defaults to 'firebase'.

    Returns:
        list: Locations of file partitions stored at filepath.
    """
    partitionLocations = []
    if database == 'firebase':
        exists, _, is_file = check_if_exists(filepath)
        if exists:
            name_ref = firebase_connect('name/' + filepath)
            partitionLocations = name_ref.get()
            if not isinstance(partitionLocations, list):
                logger.error(f"Filepath: '{filepath}' is a directory, only accepts files.")
                partitionLocations = []
        else:
            logger.error(f"File '{filepath}' does not exist!")
    else:
        raise NotImplementedError("SQL has not been implemented for this function")

    assert partitionLocations, f"No partition locations did you supply a directory instead of a filepath?"    

    return partitionLocations


def readPartition(filepath: str, k: int, database='firebase', getPartitionLocations: bool=False) -> str:
    """Get the k-th element of the partition of file, and then get the contents of that location in the selected database.

    Args:
        filepath (str): Logical path to file in database from root.
        k (int): Index of partition to get
        database (str, optional): Database implementation to use for this command. Defaults to 'firebase'.
        getPartitionLocations (bool, optional): If the functions should get the location of the partitions before reading. Ideally the user provides this information, defaults to False.
                                                Setting this value to true will increase the number of reads!
    Returns:
        dict: Object at partition k at the filepath.
    """
    location = filepath

    try:
        k = int(k)
    except ValueError:
        raise ValueError(f"'k' must be an integer, or an object that can be converted to an integer. Received {k} of type {type(k)}")

    if getPartitionLocations:
        partitionLocations = getPartitionLocations(filepath, database)
        if k >= len(partitionLocations):
            raise ValueError(f"Given k ({k}) is too large. Data has {len(partitionLocations)} partitions. Remember lists are 0-indexed!")
        location = partitionLocations[k] # location should be guaranteed to exist if our functions are correct

    if database == 'firebase':
        ref = db.reference(location)
        partition = ref.get()

        # Ugly fix for non consistent reads
        if isinstance(partition, list):
            partition = [i for i in partition if i is not None] # Sometimes list has nones
            keys = ref.get(shallow=True)
            shallow = dict(sorted(keys.items()))                # Shallow list is sometimes unsorted
            _partition = {}
            for i, key in zip(range(len(partition)), shallow.keys()):
                _partition.update({key: partition[i]})
            partition = _partition

    else:
        raise NotImplementedError("SQL has not been implemented for this function")

    return partition
