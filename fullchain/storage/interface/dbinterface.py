import binascii

from fullchain.logs.logging import log_manager
from fullchain.storage.interface.dbproperties import DBProperties

logger = log_manager.getLogger()


class DBInterface(object):

    def __init__(self, db, prefix, class_ref):
        self._built_keys = False
        self.DebugStorage = False

        self.DB = db
        self.Prefix = prefix
        self.ClassRef = class_ref

        self.Collection = {}
        self.Changed = []
        self.Deleted = []

        self._ChangedResetState = []
        self._DeletedResetState = []

        self._batch_changed = {}
        self.tracking = []

    @property
    def Current(self):
        try:
            ret = {}
            for key, val in self.Collection.items():
                if val is not None:
                    ret[key] = val
            return ret
        except Exception as e:
            logger.error("error getting items %s " % e)

        return {}

    @property
    def Keys(self):
        if not self._built_keys:
            self._BuildCollectionKeys()

        return self.Collection.keys()

    def _BuildCollectionKeys(self):
        with self.DB.openIter(DBProperties(self.Prefix, include_value=False)) as it:
            for key in it:
                key = key[1:]
                if key not in self.Collection.keys():
                    self.Collection[key] = None

    def Commit(self, wb, destroy=True):
        for keyVal in self.Changed:
            item = self.Collection[keyVal]
            if item:
                if not wb:
                    self.DB.write(self.Prefix + keyVal, self.Collection[keyVal].ToByteArray())
                else:
                    wb.put(self.Prefix + keyVal, self.Collection[keyVal].ToByteArray())
        for keyVal in self.Deleted:
            if not wb:
                self.DB.delete(self.Prefix + keyVal)
            else:
                wb.delete(self.Prefix + keyVal)
            self.Collection[keyVal] = None
        if destroy:
            self.Destroy()
        else:
            self.Changed = []
            self.Deleted = []
            self._ChangedResetState = []
            self._DeletedResetState = []

    def Reset(self):
        self.Changed = []
        self.Deleted = []

        self._ChangedResetState = []
        self._DeletedResetState = []

    def GetAndChange(self, keyVal, newInstance=None, debug_item=False):
        item = None
        if keyVal in self.Collection:
            # if deleted in this batch,add again and mark it changed
            if keyVal in self.Deleted:
                if newInstance is None:
                    item = self.ClassRef()
                else:
                    item = newInstance
                self.Deleted.remove(keyVal)

                self.Add(keyVal, item)
        # if not deleted
        else:
            item = self.TryGet(keyVal)

            if item is None:
                if newInstance is None:
                    item = self.ClassRef()
                else:
                    item = newInstance

                self.Add(keyVal, item)

            self.MarkChanged(keyVal)

        return item

    def ReplaceOrAdd(self, keyVal, newInstance):
        item = newInstance
        if keyVal in self.Deleted:
            self.Deleted.remove(keyVal)

        self.Add(keyVal, item)

        return item

    def GetOrAdd(self, keyVal, newInstance):
        existing = self.TryGet(keyVal)

        if existing:
            return existing

        item = newInstance

        if keyVal in self.Deleted:
            self.Deleted.remove(keyVal)

        self.Add(keyVal, item)

        return item

    def TryGet(self, keyVal):
        if keyVal in self.Deleted:
            return None

        if keyVal in self.Collection.keys():
            item = self.Collection[keyVal]
            if item is None:
                item = self._GetItem(keyVal)
            return item

        # otherwise, check in the database
        key = self.DB.get(self.Prefix + keyVal)

        # if the key is there, get the item
        if key is not None:
            item = self._GetItem(keyVal)
            return item

        return None

    def _GetItem(self, keyVal):
        if keyVal in self.Deleted:
            return None

        try:
            buffer = self.DB.get(self.Prefix + keyVal)
            if buffer:
                item = self.ClassRef.DeserializeFromDB(binascii.unhexlify(buffer))
                self.Collection[keyVal] = item
                return item
            return None
        except Exception as e:
            logger.error("Could not deserialize item from key %s : %s" % (keyVal, e))

        return None

    def Add(self, keyVal, item):
        if self.Prefix == b'\x70':  # Storage Prefix
            found = self.DB.get(self.Prefix + keyVal) is not None

            if not found:
                self.tracking.append(
                    {"state": "Added", "key": binascii.hexlify(keyVal).decode(), "value": item.ToByteArray().decode()})
            else:
                self.tracking.append({"state": "Changed", "key": binascii.hexlify(keyVal).decode(),
                                      "value": item.ToByteArray().decode()})

        self.Collection[keyVal] = item
        self.MarkChanged(keyVal)

    def Remove(self, keyVal):
        if keyVal not in self.Deleted:
            self.Deleted.append(keyVal)
            if self.Prefix == b'\x70':  # Storage Prefix
                self.tracking.append({"state": "Deleted", "key": binascii.hexlify(keyVal).decode(), "value": ""})

    def MarkForReset(self):
        self._ChangedResetState = self.Changed
        self._DeletedResetState = self.Deleted

    def MarkChanged(self, keyVal):
        if keyVal not in self.Changed:
            self.Changed.append(keyVal)

    def TryFind(self, key_prefix):
        candidates = {}
        for keyVal in self.Collection.keys():
            # See if we find a partial match in the keys that not have been committed yet, excluding those that are 
            # to be deleted 
            if key_prefix in keyVal and keyVal not in self.Deleted:
                candidates[keyVal[20:]] = self.Collection[keyVal].Value

        db_results = self.Find(key_prefix)

        # {**x, **y} merges two dictionaries, with the values of y overwriting the vals of x
        # withouth this merge, you sometimes get 2 results for each key
        # then take the dict and make a list of tuples
        final_collection = [(k, v) for k, v in {**db_results, **candidates}.items()]

        return iter(final_collection)

    def Find(self, key_prefix):
        key_prefix = self.Prefix + key_prefix
        res = {}
        with self.DB.openIter(DBProperties(key_prefix, include_value=True)) as it:
            for key, val in it:
                # we want the storage item, not the raw bytes
                item = self.ClassRef.DeserializeFromDB(binascii.unhexlify(val)).Value
                # also here we need to skip the 1 byte storage prefix
                res_key = key[21:]
                res[res_key] = item
        return res

    def Destroy(self):
        self.DB = None
        self.Collection = None
        self.ClassRef = None
        self.Prefix = None
        self.Deleted = []
        self.Changed = []
        self._ChangedResetState = []
        self._DeletedResetState = []
        self.tracking = []
