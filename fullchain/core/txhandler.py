import copy
import decimal

from fullchain.core.utxo import UTXO, UTXOPool
from fullchain.core.transaction import Transaction
from fullchain.core.crypto import Crypto

class TxHandler:
    def __init__(self, pool: UTXOPool):
        self._pool = pool

    def isValidTx(self, tx: Transaction) -> bool:
        inputSum = decimal.Decimal()
        pool = copy.deepcopy(self._pool)
        for (index, inp) in enumerate(tx.inputs):
            utxo = UTXO(inp.prevTxHash, inp.outputIndex)

            if not pool.contains(utxo):
                return False

            output = pool.getTxOutput(utxo)

            pubKey = output.address
            message = tx.getRawDataToSign(index)
            if not Crypto.verifySignature(pubKey, message, inp.signature):
                return False

            inputSum += output.value
            pool.removeUTXO(utxo)

        outputSum = decimal.Decimal()
        for out in tx.outputs:
            if out.value < 0:
                return False
            outputSum += out.value

        return inputSum >= outputSum


    def handleTxs(self, txs):
        result = []
        for tx in txs:
            if self.isValidTx(tx):
                result.append(tx)

                for inp in tx.inputs:
                    utxo = UTXO(inp.prevTxHash, inp.outputIndex)
                    self._pool.removeUTXO(utxo)

                for (i, out) in enumerate(tx.outputs):
                    utxo = UTXO(tx.hash, i)
                    self._pool.addUTXO(utxo, out)


        return result
