from fullchain.core.txhandler import TxHandler
from fullchain.core.transaction import Transaction 
from fullchain.core.block import Block
from fullchain.core.blockchain import BlockChain
from fullchain.core.pow import *
from fullchain.storage.leveldb.leveldbimpl import *
from Cryptodome.PublicKey import RSA
from fullchain.core.account import *



class BlockHandler:
    def __init__(
        self,
        privateKey: RSA.RsaKey,
    ):
        genesisBlk = self.getGenesisBlock()
        self.database = LevelDBImpl()
        print(genesisBlk.getHash())
        self._blockchain = BlockChain(genesisBlk)
        self._privateKey = privateKey

    def validateBlock(self, block: Block):
        if block is None:
            return False
        parent = self._blockchain.state.GetViewByHash(block._prevBlockHash)
        if parent is None:
            return False
        utxsPool = parent._utxos
        ok = validate_proof_of_work(parent._blk.nonce, parent._blk.getHash(), block._nonce, BlockChain.DIFFICULTY)
        if ok == True:
            handler = TxHandler(utxsPool)
            validTxs = handler.handleTxs(block.getTransactions())
            if len(validTxs) == len(block.getTransactions()):
                return True
        return False

    def createBlock(self, difficulty):
        selfAddress = self._privateKey.public_key()
        parent = self._blockchain.getMaxHeightBlock()
        prevHash = parent._hash
        utxoPool = self._blockchain.getMaxHeightUTXOPool()
        txsPool = self._blockchain.getTransactionPool()
        txs = txsPool.getTransactions()
        handler = TxHandler(utxoPool)
        validTxs = handler.handleTxs(txs)
        
        current = Block(
            prevHash,
            selfAddress,
            validTxs,
            parent._height + 1,
            None,
            parent._nonce
        )
        nonce = generate_proof_of_work(parent, BlockChain.DIFFICULTY)
        current._nonce = nonce
        current.finalize()
        if self._blockchain.addBlock(current):
            return current
        return None

    def processTx(self, tx: Transaction):
        self._blockchain.addTransaction(tx)

    def getGenesisBlock(self):
        md = hashlib.sha256()
        md.update(b'\x00')
        prevHash = md.digest()
        genesisPublicKey = RSA.import_key(open('genesis_public.pem', 'r').read())
        nonce= 13
        return Block(
            prevHash,
            genesisPublicKey,
            [],
            1,
            None,
            nonce,
        )


