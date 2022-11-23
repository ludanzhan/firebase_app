import firebase_admin
import json
from firebase_admin import credentials
from firebase_admin import db

database_url = 'https://dsci-551-project-177ec-default-rtdb.firebaseio.com/'
cred = credentials.Certificate('secrets/dsci-551-project-177ec-firebase-adminsdk-q5gxp-70d290b8aa.json')
# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': database_url
})


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


print(db.reference('/').get(shallow=True))



'''
if(db.reference(f'/{f[0]}').get is None):
    db.reference(f'/{f}').update(str_to_dict(s))
else:
    file =''
    for i in f[1:]:
        file = file + i+'/'
    db.reference(f'/{f[0]}').update(str_to_dict(s))
'''



    
