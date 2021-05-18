import importlib
import struct
import sys


class BinaryReader(object):
    """docstring for BinaryReader"""

    def __init__(self, stream):
        """
        Create an instance.
        Args:
            stream (BytesIO): a stream to operate on. i.e. a neo.IO.MemoryStream or raw BytesIO.
        """
        super(BinaryReader, self).__init__()
        self.stream = stream

    def unpack(self, fmt, length=1):
        """
        Unpack the stream contents according to the specified format in `fmt`.
        Args:
            fmt (str): format string.
            length (int): amount of bytes to read.
        Returns:
            variable: the result according to the specified format.
        """
        return struct.unpack(fmt, self.stream.read(length))[0]

    def readByte(self):
        """
        Read a single byte.
        Returns:
            bytes: a single byte if successful.
        Raises:
            ValueError: if there is insufficient data
        """
        return self.safeReadBytes(1)

    def readBytes(self, length):
        """
        Read the specified number of bytes from the stream.
        Args:
            length (int): number of bytes to read.
        Returns:
            bytes: `length` number of bytes.
        """
        value = self.stream.read(length)
        return value

    def safeReadBytes(self, length):
        """
        Read exactly `length` number of bytes from the stream.
        Returns:
            bytes: `length` number of bytes
        Raises:
            ValueError: if there is insufficient data
        """
        data = self.readBytes(length)
        if len(data) < length:
            raise ValueError("Not enough data available")
        else:
            return data

    def readBool(self):
        """
        Read 1 byte as a boolean value from the stream.
        Returns:
            bool:
        """
        return self.unpack('?')

    def readChar(self):
        """
        Read 1 byte as a character from the stream.
        Returns:
            str: a single character.
        """
        return self.unpack('c')

    def readFloat(self, endian="<"):
        """
        Read 4 bytes as a float value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            float:
        """
        return self.unpack("%sf" % endian, 4)

    def readDouble(self, endian="<"):
        """
        Read 8 bytes as a double value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            float:
        """
        return self.unpack("%sd" % endian, 8)

    def readInt8(self, endian="<"):
        """
        Read 1 byte as a signed integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sb' % endian)

    def readUInt8(self, endian="<"):
        """
        Read 1 byte as an unsigned integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sB' % endian)

    def readInt16(self, endian="<"):
        """
        Read 2 byte as a signed integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sh' % endian, 2)

    def readUInt16(self, endian="<"):
        """
        Read 2 byte as an unsigned integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sH' % endian, 2)

    def readInt32(self, endian="<"):
        """
        Read 4 bytes as a signed integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%si' % endian, 4)

    def readUInt32(self, endian="<"):
        """
        Read 4 bytes as an unsigned integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sI' % endian, 4)

    def ReadInt64(self, endian="<"):
        """
        Read 8 bytes as a signed integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sq' % endian, 8)

    def readUInt64(self, endian="<"):
        """
        Read 8 bytes as an unsigned integer value from the stream.
        Args:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int:
        """
        return self.unpack('%sQ' % endian, 8)

    def readVarInt(self, max=sys.maxsize):
        """
        Read a variable length integer from the stream.
        Args:
            max (int): (Optional) maximum number of bytes to read.
        Returns:
            int:
        Raises:
            ValueError: if the specified `max` number of bytes is exceeded
        """
        try:
            fb = self.readByte()
        except ValueError:
            return 0
        value = 0
        if fb == b'\xfd':
            value = self.readUInt16()
        elif fb == b'\xfe':
            value = self.readUInt32()
        elif fb == b'\xff':
            value = self.readUInt64()
        else:
            value = int.from_bytes(fb, "little")

        if value > max:
            raise ValueError(f"Maximum number of bytes ({max}) exceeded.")

        return int(value)

    def readVarBytes(self, max=sys.maxsize):
        """
        Read a variable length of bytes from the stream.
        Args:
            max (int): (Optional) maximum number of bytes to read.
        Raises:
            ValueError: if the amount of bytes indicated by the variable int cannot be read
        Returns:
            bytes:
        """
        length = self.readVarInt(max)
        return self.safeReadBytes(length)

    def readString(self):
        """
        Read a string from the stream.
        Returns:
            str:
        """
        length = self.readUInt8()
        return self.unpack(str(length) + 's', length)

    def readVarString(self, max=sys.maxsize):
        """
        Similar to `readString` but expects a variable length indicator instead of the fixed 1 byte indicator.
        Args:
            max (int): (Optional) maximum number of bytes to read.
        Returns:
            bytes:
        """
        length = self.readVarInt(max)
        return self.unpack(str(length) + 's', length)

    def readFixedString(self, length):
        """
        Read a fixed length string from the stream.
        Args:
            length (int): length of string to read.
        Returns:
            bytes:
        """
        return self.readBytes(length).rstrip(b'\x00')

    def readSerializableArray(self, class_name, max=sys.maxsize):
        """
        Deserialize a stream into the object specific by `class_name`.
        Args:
            class_name (str): a full path to the class to be deserialized into. e.g. 'neo.Core.Block.Block'
            max (int): (Optional) maximum number of bytes to read.
        Returns:
            list: list of `class_name` objects deserialized from the stream.
        """
        module = '.'.join(class_name.split('.')[:-1])
        klassname = class_name.split('.')[-1]
        klass = getattr(importlib.import_module(module), klassname)
        length = self.readVarInt(max=max)
        items = []
        for i in range(0, length):
            try:
                item = klass()
                item.deserialize(self)
                items.append(item)
            except Exception:
                continue

        return items

    def readHashes(self):
        """
        Read Hash values from the stream.
        Returns:
            list: a list of hash values. Each value is of the bytearray type.
        """
        len = self.readVarInt()
        items = []
        for i in range(0, len):
            ba = bytearray(self.readBytes(32))
            ba.reverse()
            items.append(ba.hex())
        return items
