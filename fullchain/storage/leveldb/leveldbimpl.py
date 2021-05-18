import threading
from contextlib import contextmanager

import plyvel

from fullchain.logs.logging import log_manager
from fullchain.storage.dbabstract import DBAbstract
from storage import settings

logger = log_manager.getLogger()


class LevelDBImpl(DBAbstract):
    # the instance of the database
    _db = None
    _lock = threading.RLock()

    def __init__(self, path=None):
        try:
            if not path:
                path = settings.DATABASE_PATH

            self._path = path
            self._db = plyvel.DB(self._path, create_if_missing=True,
                                 max_open_files=100,
                                 lru_cache_size=10 * 1024 * 1024)
            logger.info("Connected DB at %s " % self._path)
        except Exception as e:
            raise Exception("leveldb exception [ %s ]" % e)

    def write(self, key, value):
        self._db.put(key, value)

    def get(self, key, default=None):
        return self._db.get(key, default)

    def delete(self, key):
        self._db.delete(key)

    def createSnapshot(self):
        raise NotImplementedError

    @contextmanager
    def openIter(self, properties):
        _iter = self._db.iterator(
            prefix=properties.prefix,
            include_value=properties.include_value,
            include_key=properties.include_key)

        yield _iter
        _iter.close()

    @contextmanager
    def getBatch(self):

        with self._lock:
            _batch = self._db.write_batch()
            yield _batch
            _batch.write()

    def getPrefixedDB(self, prefix):
        return PrefixedLevelDBImpl(self._db.prefixed_db(prefix))

    def closeDB(self):
        self._db.close()


class PrefixedLevelDBImpl(LevelDBImpl):
    def __init__(self, prefixed_db, path=None):
        super().__init__(path)
        self._db = prefixed_db
