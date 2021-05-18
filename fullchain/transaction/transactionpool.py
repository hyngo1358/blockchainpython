from transaction import Transaction

class TransactionPool:
    def __init__(self):
        self._map = dict()
    
    def addTransaction(self, tx: Transaction):
        self._map[tx.hash] = tx

    def removeTransaction(self, txHash):
        self._map.pop(txHash)

    def getTransaction(self, txHash):
        return self._map.get(txHash)

    def getTransactions(self):
        return list(self._map.values())
