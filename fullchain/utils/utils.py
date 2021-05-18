import decimal

def decimal_to_bytes(x: decimal.Decimal) -> bytes:
    # Format decimal consistently, for hashing.
    # This ensures a == b <=> decimal_to_bytes(a) == decimal_to_bytes(b)
    sign, digits, exp = x.normalize().as_tuple()
    sign = ["", "-"][sign]
    digits = "".join(map(str, digits))
    return bytes(f"{sign}{digits}E{exp}", encoding="ascii")

def int_to_bytes(s: int) -> bytes:
    return bytes(str(s), encoding="ascii")
