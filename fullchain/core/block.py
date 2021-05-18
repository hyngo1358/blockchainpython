import binascii
import collections
import hashlib
import math

from fullchain.core.base import Model
from fullchain.core.exceptions import BlockInvalidException, BlockSerializeException
from fullchain.core.transaction import Transaction
from fullchain.io.binaryreader import BinaryReader
from fullchain.io.binarywriter import BinaryWriter


class Block(Model):
    COINBASE = 25

    def __init__(
            self,
            prevBlockHash: bytes = None,
            address=None,
            txs=None,
            height: int = None,  # Additional field
            hash: bytes = None,
            nonce: int = None,
    ):

        coinbase = Transaction.NewCoinbase(Block.COINBASE, address)

        self._coinbase = coinbase
        
        self._prevBlockHash = prevBlockHash
        self._height = height
        if txs is None:
            self._txs = []
        else:
            self._txs = txs
        if hash is None:
            self._hash = []
        else:
            self._hash = hash
        if nonce is None:
            self._nonce = 0
        else:
            self._nonce = nonce
        self.finalize()


    
    def getCoinbase(self):
        return self._coinbase

    
    def getHash(self):
        return self._hash

    
    def getPrevBlockHash(self):
        return self._prevBlockHash

    
    def getTransactions(self):
        return self._txs

    
    def getHeight(self):
        return self._height

    def getTransaction(self, index):
        return self._txs[index]

    
    def getNonce(self):
        return self._nonce

    def addTransaction(self, tx):
        self._txs.append(tx)

    def getRawBlock(self):
        rawBlock = b""
        rawBlock += self._prevBlockHash
        
        number_of_bytes = int(math.ceil(self._nonce.bit_length() / 8))
        rawBlock += (self._nonce).to_bytes(number_of_bytes, 'big')
        rawBlock += (self._height).to_bytes(2, 'big')
        rawBlock += self._coinbase.getRawTx()
        for tx in self._txs:
            rawBlock += tx.getRawTx()
        return rawBlock

    def finalize(self):
        md = hashlib.sha256()
        md.update(self.getRawBlock())
        self._hash = md.digest()

    
    def isGenesis(self) -> bool:
        return self.getPrevBlockHash is None

    
    def isValid(self) -> bool:
        md = hashlib.sha256()
        md.update(self.getRawBlock())
        hashed_raw_block = md.digest()
        return self.getHash == hashed_raw_block

    
    def __dict__(self) -> dict:
        if not self.isValid:
            raise BlockInvalidException

        unordered = {
            'prevBlock': binascii.hexlify(self.getPrevBlockHash).decode('ascii'),
            'nonce': self.getNonce,
            'coinbase': self.getCoinbase.__dict__,
            'height': self.getHeight,
            'transactions': [tx.__dict__ for tx in self.getTransactions()]
        }
        return collections.OrderedDict(sorted(unordered.items()))

    def serialize(self, writer: BinaryWriter):
        writer.writeBytes(self.getPrevBlockHash)
        self.getCoinbase().serialize(writer)
        writer.writeBool(self.getCoinbase)
        writer.writeUInt32(self.getHeight)
        writer.writeUInt32(self.getNonce)
        writer.writeSerializableArray(self.getTransactions)

    def deserialize(self, reader: BinaryReader):
        self._prevBlockHash = reader.readBytes(32)
        coinbase = Transaction()
        coinbase.deserialize(reader)
        self._coinbase = coinbase
        self._height = reader.readUInt32()
        self._nonce = reader.readUInt32()
        self._txs = []
        transaction_length = reader.readVarInt()

        for i in range(0, transaction_length):
            txn = Transaction()
            txn = txn.deserialize(reader)
            self._txs.append(txn)

        if self.isValid:
            raise BlockSerializeException
