from fullchain.core.utxo import UTXO, UTXOPool
from fullchain.core.block import Block

def getUTXOPoolFromBlk(blk: Block):
    res = UTXOPool()
    txs = blk.getTransactions()
    txs.append(blk.getCoinbase())
    for tx in blk._txs:
        txHash = tx.hash
        for idx, output in enumerate(blk._coinbase.outputs, start=1):
            utxo = UTXO(txHash, idx)
            res.addUTXO(utxo,output)
    return res
        
class BlockChainState:
    class View:
        def __init__(
            self,
            utxoPool: UTXOPool,
            blk: Block,
        ):
            self._utxos = utxoPool
            self._blk = blk
        
        @property 
        def utxos(self):
            return self._utxos

        @property
        def height(self):
            return self._blk._height
            
        @property
        def hash(self):
            return self._blk._hash

        @property
        def blk(self):
            return self._blk

    def __init__(
        self,
        genesisBlock: Block,
    ):
        self._viewByHash = dict()
        self._blkHashByHeight = dict()
        self._blkHashByPrevHash = dict()
        blkUTXOs = getUTXOPoolFromBlk( genesisBlock)
        view = BlockChainState.View(blkUTXOs, genesisBlock)
        self._viewByHash[genesisBlock.getHash] = view
        self._blkHashByHeight[genesisBlock._height] = [genesisBlock.getHash]
        self._blkHashByPrevHash[genesisBlock._prevBlockHash] = [genesisBlock.getHash]
        self._latestView = view
        self._finalView = self._latestView
        
        return

    def AddView(
        self,
        newBlk: Block,
    ):
        print(newBlk.getPrevBlockHash())
        print(newBlk._hash)
        blkUTXOs = getUTXOPoolFromBlk(newBlk)
        prevView = self._viewByHash[newBlk._prevBlockHash]
        viewUTXOPool = blkUTXOs._map.update(prevView._utxos._map)
        view = BlockChainState.View(viewUTXOPool, newBlk)
        self._viewByHash[newBlk._hash] = view
        self._blkHashByHeight[newBlk._height] = [newBlk._hash]
        self._blkHashByPrevHash[newBlk._prevBlockHash] = [newBlk._hash]
        return view

    def DeleteBranch(
        self,
        rootHeight: int,
        rootHash: bytes,
    ):
        removedHashes = [rootHash]
        removedHeight = rootHeight
        while True:
            tmp = removedHashes
            removedHashes = []
            for bhash in tmp:
                self._blkHashByHeight[removedHeight].remove(bhash)
                self._viewByHash.pop(bhash)
                removedHashes += self._blkHashByPrevHash.get(bhash)
                self._blkHashByPrevHash.pop(bhash)
            if len(removedHashes)==0: 
                break
            removedHeight+=1

    def UpdateFinalView(
        self,
        blkHash: bytes,
        blkHeight: int,
    ):
        for bheight in range(self._finalView._height, blkHeight):
            for bhash in self._blkHashByHeight.get(bheight):
                self._viewByHash.pop(bhash)
                self._blkHashByPrevHash.pop(bhash)
            self._blkHashByHeight.pop(bheight)

        for bhash in self._blkHashByHeight.get(blkHeight):
            if bhash != blkHash:
                self.DeleteBranch(blkHeight, bhash)
        return
    
    def UpdateLatestView(
        self,
        blkHash: bytes,
    ):
        self._latestView = self._viewByHash[blkHash]
        return 

    @property
    def finalView(self):
        return self._finalView
    
    @property
    def latestView(self):
        return self._latestView

    def GetViewByHash(self, blkHash: bytes):
        return self._viewByHash.get(blkHash)
