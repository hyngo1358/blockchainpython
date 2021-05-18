import binascii
import collections
import hashlib
from decimal import *

from Cryptodome.PublicKey import RSA

from fullchain.core.base import Model
from fullchain.core.exceptions import TransactionSerializeException
from fullchain.core.utils import int_to_bytes, decimal_to_bytes
from fullchain.core.utxo import UTXO
from fullchain.io.binaryreader import BinaryReader
from fullchain.io.binarywriter import BinaryWriter


class Input(Model):
    def __init__(self, prevHash: bytes = None, index: int = None, signature: bytes = None):
        if prevHash is None:
            self._prevTxHash = b""
        else:
            self._prevTxHash = prevHash

        if index is None:
            self._outputIndex = 0
        else:
            self._outputIndex = index

        if signature is None:
            self._signature = b""
        else:
            self._signature = signature

    @property
    def prevTxHash(self):
        # Hash of the Transaction whose output is being used
        return self._prevTxHash

    @property
    def outputIndex(self):
        # Used output's index in the previous transaction
        return self._outputIndex

    @property
    def signature(self):
        # The signature produced to check validity
        return self._signature

    def __eq__(self, other):
        if isinstance(other, Input):
            return (self.prevTxHash == other.prevTxHash
                    and self.outputIndex == other.outputIndex
                    and self.signature == other.signature)

        return False

    def __hash__(self):
        return hash((self.prevTxHash, self.outputIndex, self.signature))

    def addSignature(self, sig: bytes):
        self._signature = sig

    @property
    def __dict__(self) -> dict:
        unordered = {
            'prevTxHash': binascii.hexlify(self.prevTxHash).decode('ascii'),
            'outputIndex': self.outputIndex,
            'signature': binascii.hexlify(self.signature).decode('ascii')

        }
        return collections.OrderedDict(sorted(unordered.items()))

    def serialize(self, writer: BinaryWriter):
        writer.writeBytes(self.prevTxHash)
        writer.writeUInt8(self.outputIndex)
        writer.writeBytes(self.signature)

    def deserialize(self, reader: BinaryReader):
        self._prevTxHash = reader.readBytes(32)
        self._outputIndex = reader.readUInt8()
        self._signature = reader.readBytes(128)


class Output(Model):
    def __init__(self, v: str = None, pk=None):
        # use decimal to avoid 0.1 + 0.2 != 0.3 problem
        if v is None:
            self._value = Decimal('0')
        else:
            self._value = Decimal(str(v))
        if isinstance(pk, RSA.RsaKey):
            self._address = pk
        elif pk is not None:
            self._address = RSA.importKey(binascii.unhexlify(pk))
        else:
            self._address = None

    @property
    def value(self):
        # Output value
        return self._value

    @property
    def address(self):
        # The public key that receives this output
        return self._address

    def __eq__(self, other):
        if isinstance(other, Output):
            return (self.value == other.value
                    and self.address == other.address)

        return False

    def __hash__(self):
        return hash((self.value, self.address.e, self.address.n))

    @property
    def __dict__(self) -> dict:
        unordered = {
            'value': str(self.value),
            'address': binascii.hexlify(self.address.exportKey(format='DER')).decode('ascii')
        }
        return collections.OrderedDict(sorted(unordered.items()))

    def serialize(self, writer: BinaryWriter):
        writer.writeVarString(str(self.value))
        writer.writeVarBytes(self.address.exportKey(format='DER'))

    def deserialize(self, reader: BinaryReader):
        valueStr = reader.readVarString().decode('utf8')
        self._value = Decimal(valueStr)
        self._address = RSA.importKey(reader.readVarBytes())


class Transaction(Model):

    def __init__(self, tx=None):
        if tx is None:
            self._inputs = []
            self._outputs = []
            self._hash = None
        else:
            self._inputs = tx.inputs
            self._outputs = tx.outputs
            self._hash = tx.hash
        self._coinbase = False

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @property
    def hash(self):
        return self._hash

    @property
    def coinbase(self):
        return self._coinbase

    @property
    def __dict__(self) -> dict:
        unordered = {
            'inputs': [input.__dict__ for input in self.inputs],
            'outputs': [output.__dict__ for output in self.outputs],
            'coinbase': self.coinbase
        }
        return collections.OrderedDict(sorted(unordered.items()))

    def __eq__(self, other):
        if isinstance(other, Transaction):
            return (self.inputs == other.inputs
                    and self.outputs == other.outputs)

        return False

    def __hash__(self):
        return hash((self._inputs, self._outputs))

    def addInput(self, prevTxHash, outputIndex):
        inp = Input(prevTxHash, outputIndex)
        self._inputs.append(inp)

    def addOutput(self, value, address):
        op = Output(value, address)
        self._outputs.append(op)

    def addSignature(self, signature, index):
        self._inputs[index].addSignature(signature)

    def removeInput(self, index: int):
        if index >= len(self._inputs):
            raise AttributeError("Index out of range")
        self._inputs = self._inputs[:index] + self._inputs[index + 1:]

    def removeInputWithUTXO(self, ut: UTXO):
        for index, inp in enumerate(self._inputs):
            u = UTXO(inp.prevTxHash, inp.outputIndex)
            if u == ut:
                self._inputs = self._inputs[:index] + self._inputs[index + 1:]
                return

    def getRawDataToSign(self, index: int) -> bytes:
        # produces data repr for  ith=index input and all outputs
        sigData = b""
        if index > len(self._inputs):
            return sigData

        inp = self.inputs[index]
        sigData += inp.prevTxHash
        sigData += int_to_bytes(inp.outputIndex)

        for op in self.outputs:
            sigData += decimal_to_bytes(op.value)
            # using pycryptodome lib
            # e: RSA public exponent
            sigData += int_to_bytes(op.address.e)
            # n: RSA modulus
            sigData += int_to_bytes(op.address.n)

        return sigData

    def getRawTx(self) -> bytes:
        rawTx = b""
        for inp in self.inputs:
            rawTx += inp.prevTxHash
            rawTx += int_to_bytes(inp.outputIndex)
            rawTx += inp.signature

        for op in self.outputs:
            rawTx += decimal_to_bytes(op.value)
            rawTx += int_to_bytes(op.address.e)
            rawTx += int_to_bytes(op.address.n)

        return rawTx

    def finalize(self):
        md = hashlib.sha256()
        md.update(self.getRawTx())
        self._hash = md.digest()

    def getInput(self, index: int) -> Input:
        return self.inputs[index]

    def getOutput(self, index: int) -> Output:
        return self.outputs[index]

    def numInputs(self):
        return len(self.inputs)

    def numOutputs(self):
        return len(self.outputs)

    def isCoinbase(self):
        return self.coinbase

    @property
    def isValid(self) -> bool:
        md = hashlib.sha256()
        md.update(self.getRawTx())
        hashed_raw_txn = md.digest()
        return self.hash == hashed_raw_txn

    def serialize(self, writer: BinaryWriter):
        writer.writeSerializableArray(self.inputs)
        writer.writeSerializableArray(self.outputs)
        writer.writeBool(self.coinbase)

    def deserialize(self, reader: BinaryReader):
        self._inputs = reader.readSerializableArray('fullchain.core.transaction.Input')
        self._outputs = reader.readSerializableArray('fullchain.core.transaction.Output')
        self._coinbase = reader.readBool()

        if self.isValid:
            raise TransactionSerializeException
        return self

    # Additional method
    @staticmethod
    def NewCoinbase(value, address):
        coinbase = Transaction()
        coinbase.addOutput(value, address)
        coinbase._coinbase = True
        coinbase.finalize()
        return coinbase
