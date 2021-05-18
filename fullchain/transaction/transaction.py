
import binascii
import hashlib
from collections import OrderedDict
from decimal import *

from Cryptodome.PublicKey import RSA

from utils import int_to_bytes, decimal_to_bytes
from utxo import UTXO

class Transaction:

    class Input:
        def __init__(self, prevHash: bytes, index: int, signature: bytes = None):
            if prevHash is None:
                self._prevTxHash = b""
            else:
                self._prevTxHash = prevHash

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
            if isinstance(other, Transaction.Input):
                return (self.prevTxHash == other.prevTxHash
                        and self.outputIndex == other.outputIndex
                        and self.signature == other.signature)

            return False

        def __hash__(self):
            return hash((self.prevTxHash, self.outputIndex, self.signature))

        def addSignature(self, sig: bytes):
            self._signature = sig

        def to_dict(self):
            return OrderedDict({'prevTxHash': binascii.hexlify(self.prevTxHash).decode('ascii'),
                                'outputIndex': self.outputIndex,
                                'signature': binascii.hexlify(self.signature).decode('ascii')})


    class Output:
        def __init__(self, v, pk):
            # use decimal to avoid 0.1 + 0.2 != 0.3 problem
            self._value = Decimal(str(v))
            if isinstance(pk, RSA.RsaKey):
                self._address = pk
            else:
                self._address = RSA.importKey(binascii.unhexlify(pk))

        @property
        def value(self):
            # Output value
            return self._value

        @property
        def address(self):
            # The public key that receives this output
            return self._address

        def __eq__(self, other):
            if isinstance(other, Transaction.Output):
                return (self.value == other.value
                        and self.address == other.address)

            return False

        def __hash__(self):
            return hash((self.value, self.address.e, self.address.n))

        def to_dict(self):
            return OrderedDict({'value': self.value,
                                'address': binascii.hexlify(self.address.exportKey(format='DER')).decode('ascii')})


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

    def __eq__(self, other):
        if isinstance(other, Transaction):
            return (self.inputs == other.inputs
                    and self.outputs == other.outputs)

        return False

    def __hash__(self):
        return hash((self._inputs, self._outputs))

    def addInput(self, prevTxHash, outputIndex):
        inp = Transaction.Input(prevTxHash, outputIndex)
        self._inputs.append(inp)

    def addOutput(self, value, address):
        op = Transaction.Output(value, address)
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

    #Additional method
    @staticmethod
    def NewCoinbase(value, address):
        coinbase = Transaction()
        coinbase.addOutput(value, address)
        coinbase._coinbase = True
        coinbase.finalize()
        return coinbase
