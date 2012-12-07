_CRC64POLY = 0x142f0e1eba9ea3693

class CRC64(object):
    def __init__(self, arg=None):
        self.crc64 = 0
        if arg:
            self.update(arg)

    def update(self, arg):
        for c in bytes(arg):
            x = ord(c)
            for bit in range(8):
                if (self.crc64 & 0x80000000000000000):
                    if 1 & (x>>bit):
                        self.crc64 = ((self.crc64 << 1) ^ _CRC64POLY) % (1<<64)
                    else:
                        self.crc64 = (self.crc64 << 1) % (1<<64)
                else:
                    if not (~1) & (x>>bit):
                        self.crc64 = ((self.crc64 << 1) ^ _CRC64POLY) % (1<<64)
                    else:
                        self.crc64 = (self.crc64 << 1) % (1<<64)
