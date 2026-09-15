"""Read Lua 5.1 chunks and adapt only size_t width for a native audit VM.

This utility never rewrites instructions or numeric constants. The 32-bit
round-trip assertion is required before 64-bit serialization is accepted.
"""
import struct


class Chunk:
    def __init__(self, data):
        if data[:12] != b'\x1bLua\x51\x00\x01\x04\x04\x04\x08\x00':
            raise ValueError('Expected little-endian Lua 5.1 / 32-bit size_t')
        self.data, self.pos = data, 12
        self.root = self.read_proto()
        if self.pos != len(data) or self.serialize(4) != data:
            raise ValueError('Bytecode did not round-trip exactly')

    def take(self, count):
        result = self.data[self.pos:self.pos + count]
        if len(result) != count:
            raise ValueError('Truncated bytecode')
        self.pos += count
        return result

    def integer(self):
        return struct.unpack('<I', self.take(4))[0]

    def string(self):
        count = self.integer()
        return self.take(count) if count else b''

    def read_proto(self):
        proto = {'source': self.string(), 'lines': self.take(8), 'header': self.take(4)}
        proto['code'] = [self.take(4) for _ in range(self.integer())]
        constants = []
        for _ in range(self.integer()):
            tag = self.take(1)
            sizes = {b'\0': 0, b'\1': 1, b'\3': 8}
            constants.append((tag, self.string() if tag == b'\4' else self.take(sizes[tag])))
        proto['constants'] = constants
        proto['children'] = [self.read_proto() for _ in range(self.integer())]
        proto['debuglines'] = [self.take(4) for _ in range(self.integer())]
        proto['locals'] = [(self.string(), self.take(8)) for _ in range(self.integer())]
        proto['upvalues'] = [self.string() for _ in range(self.integer())]
        return proto

    @staticmethod
    def instruction(raw):
        word, = struct.unpack('<I', raw)
        return word & 63, (word >> 6) & 255, word >> 14

    def named_function(self, name):
        """Find the root-level CLOSURE followed by SETGLOBAL for this name."""
        target = name.encode('ascii') + b'\0'
        for index, raw in enumerate(self.root['code'][:-1]):
            op, register, child = self.instruction(raw)
            nextop, nextreg, constant = self.instruction(self.root['code'][index + 1])
            if op == 36 and nextop == 7 and register == nextreg:
                if self.root['constants'][constant] == (b'\4', target):
                    proto = self.root['children'][child]
                    if proto['header'][0] != 0:
                        raise ValueError('Cannot detach a function with upvalues')
                    return proto
        raise KeyError(name)

    def serialize(self, size_t=8, proto=None):
        out = bytearray(b'\x1bLua\x51\x00\x01\x04' + bytes([size_t]) + b'\x04\x08\x00')
        def number(value):
            out.extend(struct.pack('<I', value))
        def string(value):
            out.extend(struct.pack('<I' if size_t == 4 else '<Q', len(value)))
            out.extend(value)
        def write(value):
            string(value['source'])
            out.extend(value['lines'] + value['header'])
            number(len(value['code']))
            out.extend(b''.join(value['code']))
            number(len(value['constants']))
            for tag, constant in value['constants']:
                out.extend(tag)
                if tag == b'\4':
                    string(constant)
                else:
                    out.extend(constant)
            number(len(value['children']))
            for child in value['children']:
                write(child)
            number(len(value['debuglines']))
            out.extend(b''.join(value['debuglines']))
            number(len(value['locals']))
            for name, scope in value['locals']:
                string(name)
                out.extend(scope)
            number(len(value['upvalues']))
            for name in value['upvalues']:
                string(name)
        write(self.root if proto is None else proto)
        return bytes(out)
