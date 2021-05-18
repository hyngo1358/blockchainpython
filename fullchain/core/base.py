import json

from fullchain.io.binaryreader import BinaryReader
from fullchain.io.binarywriter import BinaryWriter
from fullchain.io.memorystream import StreamManager


class Model:
    @property
    def __dict__(self) -> dict:
        raise NotImplementedError()

    @property
    def __str__(self) -> str:
        return json.dumps(self.__dict__)

    @property
    def __bytes__(self) -> bytes:
        return self.__str__.encode()

    def serialize(self, writer: BinaryWriter):
        raise NotImplementedError()

    def deserialize(self, reader: BinaryReader):
        raise NotImplementedError()

    def toByteArray(self):
        """
        Serialize the given `value` to a an array of bytes.

        Args:
            value object extending SerializableMixin.

        Returns:
            bytes: hex formatted bytes
        """
        ms = StreamManager.getStream()
        writer = BinaryWriter(ms)
        self.serialize(writer)
        retVal = ms.toArray()
        StreamManager.releaseStream(ms)
        return retVal
