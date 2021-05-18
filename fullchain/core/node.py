import multiprocessing
from fullchain.core.rpc import *
from fullchain.storage.leveldb.leveldbimpl import *

def start_node(hostport='0.0.0.0:3009'):
    init_node()
    print('INFO', 'Node initialize success.')
    try:
        if hostport.find('.') != -1:
            host,port = hostport.split(':')
        else:
            host = '0.0.0.0'
            port = hostport
    except Exception:
        print('ERROR','params must be {port} or {host}:{port} , ps: 3009 or 0.0.0.0:3009')
    p = multiprocessing.Process(target=start_server,args=(host,int(port)))
    p.start()
    print('INFO','Node start success. Listen at %s.' % (hostport,))

def init_node():
    """
    Download blockchain from node compare with local database and select the longest blockchain.
    """
    all_node_blockchains = BroadCast().get_blockchain()
    all_node_txs = BroadCast().get_transactions()
    bcdb = LevelDBImpl()
    txdb = LevelDBImpl()
    blockchain = bcdb.getBatch()
    transactions = txdb.getBatch()
    # If there is a blochain downloaded longer than local database then relace local's.
    # for bc in all_node_blockchains:
    #     if len(bc) > len(blockchain):
    #         bcdb.write()
            
    # for txs in all_node_txs:
    #     if len(txs) > len(transactions):
    #         txdb.clear()
    #         txdb.write(txs)    

    
if __name__=='__main__':
    start_node(3009)
