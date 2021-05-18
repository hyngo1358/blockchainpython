import hashlib

def validate_proof_of_work(last_nonce, last_hash, nonce, difficulty):
    """
    Validates the nonce
    :param last_nonce: <int> Nonce of the last block
    :param nonce: <int> Current nonce to be validated
    :param last_hash: <str> Hash of the last block
    :return: <bool> True if correct, False if not.
    """
    sha = hashlib.sha256(f'{last_nonce}{last_hash}{nonce}'.encode())
    sha_str = sha.hexdigest()
    for i in range(difficulty):
        if sha_str[i] != '0':
            return False
    return True

def generate_proof_of_work(block, difficulty):
    """
    Very simple proof of work algorithm:
    - Find a number 'p' such that hash(pp') contains 4 leading zeroes
    - Where p is the previous proof, and p' is the new proof
    :param block: <Block> reference to the last block object
    :return: <int> generated nonce
    """
    last_nonce = block._nonce
    last_hash = block._hash

    nonce = 0
    while not validate_proof_of_work(last_nonce, last_hash, nonce, difficulty):
        nonce += 1

    return nonce