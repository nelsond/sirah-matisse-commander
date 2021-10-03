import struct


def data_length(str):
    """Calculates the length of string as unsigned intenger."""
    return struct.pack('>L', len(str))
