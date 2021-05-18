import hashlib
from os import path
from Cryptodome.PublicKey import RSA
# from model import Model
# from lib.common import pubkey_to_address
# from database import AccountDB


def new_account():
    x = RSA.generate(2048)
    return x

def get_account(filename):
    if len(filename) == 0:
        key = new_account()
        return key
    newaccount = RSA.import_key(open(filename, 'r').read())
    return newaccount


