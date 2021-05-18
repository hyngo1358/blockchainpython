class UTXO:
    def __init__(self, txHash: bytes, index: int):
        self._txHash = txHash
        self._index = index

    def getTxHash(self):
        return self._txHash

    def getIndex(self):
        return self._index

    def __hash__(self):
        return hash((self._index, self._txHash))

    def __eq__(self, other):
        if not isinstance(other, UTXO):
            return NotImplemented
        return self._compare(other) == 0

    def __gt__(self, other):
        if not isinstance(other, UTXO):
            return NotImplemented
        return self._compare(other) == 1

    def __lt__(self, other):
        if not isinstance(other, UTXO):
            return NotImplemented
        return self._compare(other) == -1

    def _compare(self, other):
        if self._index > other._index:
            return 1
        if self._index < other._index:
            return -1
        if self._txHash > other._txHash:
            return 1
        if self._txHash < other._txHash:
            return -1
        return 0


class UTXOPool:
    def __init__(self):
        self._map = dict()

    def addUTXO(self, utxo: UTXO, txOut):
        self._map[utxo] = txOut

    def removeUTXO(self, utxo: UTXO):
        self._map.pop(utxo)

    def getTxOutput(self, utxo: UTXO):
        return self._map.get(utxo)

    def contains(self, utxo: UTXO):
        return utxo in self._map

    def getAllUTXO(self):
        return list(self._map.keys())
