from fullchain.core.block import Block
from fullchain.core.transaction import Transaction
from fullchain.core.transactionpool import TransactionPool
from fullchain.core.txhandler import TxHandler
from fullchain.core.state import BlockChainState
# import base.transaction as tx
class BlockChain:
    CUT_OFF_AGE = 10
    DIFFICULTY = 4
    def __init__(self, genesisBlock: Block):
        #IMPLEMENT THIS
        #---SOLUTION---
        self._state = BlockChainState(genesisBlock)
        self._txPool = TransactionPool()
        return
        #---SOLUTION---

    @property
    def state(self):
        return self._state

    def getMaxHeightBlock(self):
        #IMPLEMENT THIS
        #---SOLUTION---
        return self._state._latestView._blk
        #---SOLUTION---

    def getMaxHeightUTXOPool(self):
        #IMPLEMENT THIS
        #---SOLUTION---
        return self._state._latestView._utxos
        #---SOLUTION---
    
    def getTransactionPool(self):
        #IMPLEMENT THIS
        #---SOLUTION---
        return self._txPool
        #---SOLUTION---

    def addBlock(self, blk: Block):
        #IMPLEMENT THIS
        #---SOLUTION---
        blkHeight = blk._height
        blkHash = blk._hash
        prevHash = blk._prevBlockHash
        blkTxs = blk._txs
        prevView = self._state.GetViewByHash(prevHash)
        if prevView is None:
            return False
        view = self._state.GetViewByHash(blkHash)
        if not view is None:
            return False
        if blkHeight != prevView.height + 1:
            return False
        if blkHeight > BlockChain.CUT_OFF_AGE:
            return False
        handler = TxHandler(prevView._utxos)
        validTxs = handler.handleTxs(blkTxs)
        if len(validTxs) != len(blkTxs):
            return False
        self._state.AddView(Block)
        if blkHeight >= self._state._latestView.height():
            self._state.UpdateLatestView(blkHash)
        return True
        #---SOLUTION---

    def addTransaction(self, tx: Transaction):
        #IMPLEMENT THIS
        #---SOLUTION---
        self._txPool.addTransaction(tx)
        return
        #---SOLUTION---