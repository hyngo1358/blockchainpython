class BlockInvalidException(Exception):
    """Block is invalid"""


class TransactionInvalidSignatureException(Exception):
    """Transaction has invalid signature"""


class TransactionInvalidException(Exception):
    """Transaction is invalid"""


class TransactionSerializeException(Exception):
    """Transaction can not serialize"""


class BlockSerializeException(Exception):
    """Block can not serialize"""
