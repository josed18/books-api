from graphql_relay.node.node import from_global_id
from booksapi.api import app
from cryptography.fernet import Fernet

_key = bytes(app.config['FERNEL_KEY'], 'utf-8')


def encrypt_password(password: str):
    fernet = Fernet(_key)
    encrypt_pass = fernet.encrypt(bytes(password, 'utf-8'))
    return encrypt_pass.decode('utf-8')


def check_passwod(encrypt_pass: str or None, password: str):
    if encrypt_pass is None:
        return False
    fernet = Fernet(_key)
    password_db = fernet.decrypt(bytes(encrypt_pass, 'utf-8')).decode('utf-8')
    return password_db == password

def input_to_dictionary(input):
    """Method to convert Graphene inputs into dictionary"""
    dictionary = {}
    for key in input:
        # Convert GraphQL global id to database id
        if key[-2:] == 'id':
            try:
                input[key] = int(from_global_id(input[key])[1])
            except Exception as e:
                pass
        if isinstance(input[key], str):
            input[key] = input[key].strip()
        if isinstance(input[key], list):
            input[key] = [input_to_dictionary(i) for i in input[key]]
        if isinstance(input[key], dict):
            input[key] = input_to_dictionary(input[key])
        dictionary[key] = input[key]
    return dictionary


