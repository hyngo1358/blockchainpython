import importlib

from fullchain.io.binaryreader import BinaryReader
from fullchain.io.memorystream import StreamManager
from fullchain.logs.logging import log_manager

logger = log_manager.getLogger()


class Helper:

    @staticmethod
    def AsSerializableWithType(buffer, class_name):
        """

        Args:
            buffer (BytesIO/bytes): stream to deserialize `class_name` to.
            class_name (str): a full path to the class to be deserialized into. e.g. 'fullchain.core.block.Block'

        Returns:
            object: if deserialization is successful.
            None: if deserialization failed.
        """
        module = '.'.join(class_name.split('.')[:-1])
        klassname = class_name.split('.')[-1]
        klass = getattr(importlib.import_module(module), klassname)
        mstream = StreamManager.getStream(buffer)
        reader = BinaryReader(mstream)

        try:
            serializable = klass()
            serializable.deserialize(reader)
            return serializable
        except Exception as e:
            logger.error("Could not deserialize: %s %s" % (e, class_name))
        finally:
            StreamManager.releaseStream(mstream)

        return None
