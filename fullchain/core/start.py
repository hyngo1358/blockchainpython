import multiprocessing
from fullchain.core.account import *
from fullchain.core.rpc import *
from transaction import *
from fullchain.core.block import *
from fullchain.core.blockhandler import *
import sys
from fullchain.core.node import *

import inspect

MODULES = ['miner','node']

def upper_first(string):
    return string[0].upper()+string[1:]

class Node():

    def add(self, args):
        add_node(args[0])
        BroadCast().add_node(args[0])
        print('Allnode',get_nodes())
    
    def run(self, args):
        start_node(args[0])



class Miner():
    def start(self, args):
        selfAcc = get_account('private.pem')
        if selfAcc is None:
            print('ERROR','Please create account before start miner.')
            exit()
        start_node(args[0])
        blkHandler = BlockHandler(selfAcc)
        while True:
            newBlk = blkHandler.createBlock(BlockChain.DIFFICULTY)
            print('Miner new block', newBlk.getHash())



def usage(class_name):
    module = globals()[upper_first(class_name)]
    print('  ' + class_name + '\r')
    print('    [action]\r')
    for k,v in module.__dict__.items():
        if callable(v):
            print('      %s' % (k,))
    print('\r')

def help():
    print("Usage: python console.py [module] [action]\r")
    print('[module]\n')
    for m in MODULES:
        usage(m)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        help()
        exit()
    module = sys.argv[1]
    if module == 'help':
        help()
        exit()
    if module not in MODULES:
        print('Error', 'First arg shoud in %s' % (str(MODULES,)))
        exit()
    mob = globals()[upper_first(module)]()
    method = sys.argv[2]
    try:
        getattr(mob, method)(sys.argv[3:])
    except Exception as e:
        print('ERROR','Maybe command params get wrong, please check and try again.')
