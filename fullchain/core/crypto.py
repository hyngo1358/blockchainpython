from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pkcs1_15


class Crypto:

    """
    @return true is {@code signature} is a valid digital signature of {@code message} under the
            key {@code pubKey}. Internally, this uses RSA signature, but the student does not
            have to deal with any of the implementation details of the specific signature
            algorithm
    """
    @staticmethod
    def verifySignature(pubkey: RSA.RsaKey, message: bytes, signature: bytes):
        h = SHA256.new(message)
        verifier = pkcs1_15.new(pubkey)
        try:
            verifier.verify(h, signature)
            return True
        except (ValueError, TypeError):
            return False
