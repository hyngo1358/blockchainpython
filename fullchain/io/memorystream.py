from binascii import hexlify
from io import BytesIO

__mstreams__ = []
__mstreams_available__ = []


class StreamManager:

    @staticmethod
    def totalBuffers():
        """
        Get the total number of buffers stored in the StreamManager.
        Returns:
            int:
        """
        return len(__mstreams__)

    @staticmethod
    def getStream(data=None):
        """
        Get a MemoryStream instance.
        Args:
            data (bytes, bytearray, BytesIO): (Optional) data to create the stream from.
        Returns:
            MemoryStream: instance.
        """
        if len(__mstreams_available__) == 0:
            if data:
                mstream = MemoryStream(data)
                mstream.seek(0)
            else:
                mstream = MemoryStream()
            __mstreams__.append(mstream)
            return mstream

        mstream = __mstreams_available__.pop()

        if data is not None and len(data):
            mstream.cleanUp()
            mstream.write(data)

        mstream.seek(0)

        return mstream

    @staticmethod
    def releaseStream(mstream):
        """
        Release the memory stream
        Args:
            mstream (MemoryStream): instance.
        """
        mstream.cleanUp()
        __mstreams_available__.append(mstream)


class MemoryStream(BytesIO):
    """docstring for MemoryStream"""

    def __init__(self, *args, **kwargs):
        """
        Create an instance.
        Args:
            *args:
            **kwargs:
        """
        super(MemoryStream, self).__init__(*args, **kwargs)

    def canRead(self):
        """
        Get readable status.
        Returns:
            bool: True if the stream can be read from. False otherwise.
        """
        return self.readable()

    def canSeek(self):
        """
        Get random access support status.
        Returns:
            bool: True if random access is supported. False otherwise.
        """
        return self.seekable

    def canWrite(self):
        """
        Get writeable status.
        Returns:
            bool: True if the stream is writeable. False otherwise.
        """
        return self.writable()

    def toArray(self):
        """
        Hexlify the stream data.
        Returns:
            bytes: b"" object containing the data.
        """
        return hexlify(self.getvalue())

    def cleanUp(self):
        """
        cleanUp the stream by truncating it to size 0.
        """
        self.seek(0)
        self.truncate(0)
