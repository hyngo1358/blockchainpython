from fullchain.core.exceptions import BlockInvalidException, TransactionInvalidException
from fullchain.logs.logging import log_manager
from fullchain.storage.access.blockaccessor import getBlockByHash
from fullchain.storage.dbprefix import DBPrefix

logger = log_manager.getLogger()


def getTransaction(db, txnHash):
    try:
        out = db.get(DBPrefix.DATA_TXN_INDEX + txnHash)
        if out is not None:
            out = bytearray(out)
            blockHash = out[:-4]
            index = int.from_bytes(out[-4:], 'little')

            block = getBlockByHash(db, blockHash)
            if block is None:
                raise BlockInvalidException

            if len(block.getTransactions()) <= index:
                raise TransactionInvalidException

            return block.getTransaction(index)
    except Exception as e:
        logger.error("Could not get transaction %s " % e)
    return None


def containTransaction(db, txnHash):
    return getTransaction(db, txnHash) is not None
