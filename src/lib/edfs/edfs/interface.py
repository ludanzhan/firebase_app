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
    ref = db.reference(path) # Only checking name node, if we did things right, data node should be guaranteed to exist.        
    data = ref.get()
    exists = data is not None # Something is a file if the child of the value of the child is a path
    return exists, data, is_file
