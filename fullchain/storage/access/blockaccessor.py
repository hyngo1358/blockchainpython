import binascii

from fullchain.core.block import Block
from fullchain.io.helper import Helper
from fullchain.logs.logging import log_manager
from fullchain.storage.dbprefix import DBPrefix

logger = log_manager.getLogger()


def getBlockByHash(db, blockHash):
    try:
        out = bytearray(db.get(DBPrefix.DATA_BLOCK + blockHash))
        outhex = binascii.unhexlify(out)
        return Helper.AsSerializableWithType(outhex, 'fullchain.core.block.Block')
    except Exception as e:
        logger.error("Could not get block %s " % e)
    return None


def storeTransactionIndex(db, txnHash, blockHash, txnIndex):
    try:
        with db.getBatch() as tx_wb:
            tx_wb.put(DBPrefix.DATA_TXN_INDEX + txnHash, blockHash + txnIndex.to_bytes(4, 'little'))
        return True
    except Exception as e:
        logger.error("Could not store transaction index because %s " % e)
    return False


def storeBlock(db, block: Block):
    try:
        if block.isValid:
            with db.getBatch() as blockWb:
                blockWb.put(DBPrefix.DATA_BLOCK + block.getHash(), block.toByteArray())

                for txnIdx, txn in enumerate(block.getTransactions):
                    storeTransactionIndex(db, txn.hash, block.getHash(), txnIdx)
            return True
    except Exception as e:
        logger.error("Could not store block because %s " % e)
    return False
