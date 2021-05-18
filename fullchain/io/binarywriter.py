import binascii
import struct


def swap32(i):
    """
    Change the endianness from little endian to big endian.
    Args:
        i (int):
    Returns:
        int:
    """
    return struct.unpack("<I", struct.pack(">I", i))[0]


def convert_to_uint160(value):
    """
    Convert an int value to a 10 bytes binary string value.
    Note: the return value is not really 160 bits, nor is it of the neo.Core.UInt160 type
    Args:
        value (int): number to convert.
    Returns:
        str:
    """
    return bin(value + 2 ** 20)[-20:]


def convert_to_uint256(value):
    """
    Convert an int value to a 16 bytes binary string value.
    Note: the return value is not really 256 bits, nor is it of the neo.Core.UInt256 type
    Args:
        value (int): number to convert.
    Returns:
        str:
    """
    return bin(value + 2 ** 32)[-32:]


class BinaryWriter(object):
    """docstring for BinaryWriter"""

    def __init__(self, stream):
        """
        Create an instance.
        Args:
            stream (BytesIO): a stream to operate on. i.e. a neo.IO.MemoryStream or raw BytesIO.
        """
        super(BinaryWriter, self).__init__()
        self.stream = stream

    def writeByte(self, value):
        """
        Write a single byte to the stream.
        Args:
            value (bytes, str or int): value to write to the stream.
        """
        if type(value) is bytes:
            self.stream.write(value)
        elif type(value) is str:
            self.stream.write(value.encode('utf-8'))
        elif type(value) is int:
            self.stream.write(bytes([value]))
        elif type(value) is bool:
            if value:
                self.stream.write(bytes([1]))
            else:
                self.stream.write(bytes([0]))

    def writeBytes(self, value, unhex=True):
        """
        Write a `bytes` type to the stream.
        Args:
            value (bytes): array of bytes to write to the stream.
            unhex (bool): (Default) True. Set to unhexlify the stream. Use when the bytes are not raw bytes; i.e. b'aabb'
        Returns:
            int: the number of bytes written.
        """
        if unhex:
            try:
                value = binascii.unhexlify(value)
            except binascii.Error:
                pass
        return self.stream.write(value)

    def pack(self, fmt, data):
        """
        Write bytes by packing them according to the provided format `fmt`.
        For more information about the `fmt` format see: https://docs.python.org/3/library/struct.html
        Args:
            fmt (str): format string.
            data (object): the data to write to the raw stream.
        Returns:
            int: the number of bytes written.
        """
        return self.writeBytes(struct.pack(fmt, data), unhex=False)

    def writeChar(self, value):
        """
        Write a 1 byte character value to the stream.
        Args:
            value: value to write.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('c', value)

    def writeFloat(self, value, endian="<"):
        """
        Pack the value as a float and write 4 bytes to the stream.
        Args:
            value (number): the value to write to the stream.
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sf' % endian, value)

    def writeDouble(self, value, endian="<"):
        """
        Pack the value as a double and write 8 bytes to the stream.
        Args:
            value (number): the value to write to the stream.
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sd' % endian, value)

    def writeInt8(self, value, endian="<"):
        """
        Pack the value as a signed byte and write 1 byte to the stream.
        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sb' % endian, value)

    def writeUInt8(self, value, endian="<"):
        """
        Pack the value as an unsigned byte and write 1 byte to the stream.
        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sB' % endian, value)

    def writeBool(self, value):
        """
        Pack the value as a bool and write 1 byte to the stream.
        Args:
            value: the boolean value to write.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('?', value)

    def writeInt16(self, value, endian="<"):
        """
        Pack the value as a signed integer and write 2 bytes to the stream.
        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sh' % endian, value)

    def writeUInt16(self, value, endian="<"):
        """
        Pack the value as an unsigned integer and write 2 bytes to the stream.
        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sH' % endian, value)

    def writeInt32(self, value, endian="<"):
        """
        Pack the value as a signed integer and write 4 bytes to the stream.
        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%si' % endian, value)

    def writeUInt32(self, value, endian="<"):
        """
        Pack the value as an unsigned integer and write 4 bytes to the stream.
        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sI' % endian, value)

    def writeInt64(self, value, endian="<"):
        """
        Pack the value as a signed integer and write 8 bytes to the stream.
        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sq' % endian, value)

    def writeUInt64(self, value, endian="<"):
        """
        Pack the value as an unsigned integer and write 8 bytes to the stream.
        Args:
            value:
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        return self.pack('%sQ' % endian, value)

    def writeVarInt(self, value, endian="<"):
        """
        Write an integer value in a space saving way to the stream.
        Args:
            value (int):
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        Raises:
            TypeError: if `value` is not of type int.
            ValueError: if `value` is < 0.
        """
        if not isinstance(value, int):
            raise TypeError(f'{value} not int type.')

        if value < 0:
            raise ValueError(f'{value} too small.')

        elif value < 0xfd:
            return self.writeByte(value)

        elif value <= 0xffff:
            self.writeByte(0xfd)
            return self.writeUInt16(value, endian)

        elif value <= 0xFFFFFFFF:
            self.writeByte(0xfe)
            return self.writeUInt32(value, endian)

        else:
            self.writeByte(0xff)
            return self.writeUInt64(value, endian)

    def writeVarBytes(self, value, endian="<"):
        """
        Write an integer value in a space saving way to the stream.
        Args:
            value (bytes):
            endian (str): specify the endianness. (Default) Little endian ('<'). Use '>' for big endian.
        Returns:
            int: the number of bytes written.
        """
        length = len(value)
        self.writeVarInt(length, endian)

        return self.writeBytes(value, unhex=False)

    def writeVarString(self, value, encoding="utf-8"):
        """
        Write a string value to the stream.
        Args:
            value (string): value to write to the stream.
            encoding (str): string encoding format.
        """
        if type(value) is str:
            value = value.encode(encoding)

        length = len(value)
        ba = bytearray(value)
        byts = binascii.hexlify(ba)
        string = byts.decode(encoding)
        self.writeUInt8(length)
        self.writeBytes(string)

    def writeFixedString(self, value, length):
        """
        Write a string value to the stream.
        Args:
            value (str): value to write to the stream.
            length (int): length of the string to write.
        Raises:
            ValueError: if the input `value` length is longer than the fixed `length`
        """
        towrite = value.encode('utf-8')
        slen = len(towrite)
        if slen > length:
            raise ValueError(f"String '{value}' length is longer than fixed length: {length}")
        self.writeBytes(towrite)
        diff = length - slen

        while diff > 0:
            self.writeByte(0)
            diff -= 1

    def writeSerializableArray(self, array):
        """
        Write an array of serializable objects to the stream.
        Args:
            array(list): a list of serializable objects. i.e. extending neo.IO.Mixins.SerializableMixin
        """
        if array is None:
            self.writeByte(0)
        else:
            self.writeVarInt(len(array))
            for item in array:
                item.serialize(self)

    def writeHashes(self, arr):
        """
        Write an array of hashes to the stream.
        Args:
            arr (list): a list of 32 byte hashes.
        """
        length = len(arr)
        self.writeVarInt(length)
        for item in arr:
            ba = bytearray(binascii.unhexlify(item))
            ba.reverse()
            self.writeBytes(ba)
