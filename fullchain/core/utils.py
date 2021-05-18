import binascii
import decimal

from Cryptodome.Hash import SHA256
from Cryptodome.Signature import PKCS1_v1_5


def decimal_to_bytes(x: decimal.Decimal) -> bytes:
    # Format decimal consistently, for hashing.
    # This ensures a == b <=> decimal_to_bytes(a) == decimal_to_bytes(b)
    sign, digits, exp = x.normalize().as_tuple()
    sign = ["", "-"][sign]
    digits = "".join(map(str, digits))
    return bytes(f"{sign}{digits}E{exp}", encoding="ascii")


def int_to_bytes(s: int) -> bytes:
    return bytes(str(s), encoding="ascii")


def sign(privateKey, tx, index):
    # Takes msg and sk and outputs signature for msg
    hashMsg = SHA256.new(tx.getRawDataToSign(index))
    signer = PKCS1_v1_5.new(privateKey)
    signature = signer.sign(hashMsg)
    return signature


def verify(publicKey, signature, msg):
    # Takes msg public key and signature and returns boolean
    hashMsg = SHA256.new(msg)
    verifier = PKCS1_v1_5.new(publicKey)
    try:
        verifier.verify(hashMsg, binascii.unhexlify(signature))
        return True
    except:
        return False
