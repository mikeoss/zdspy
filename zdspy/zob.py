from abc import ABC

from . import dataio as d, gheader as gh
from .helpers import debug_print


class ZOB_NPC(gh.ZDS_GenericElementHeaderRaw):
    def init(self):
        self.unknown_1 = d.UInt16(self.data, 8)
        self.unknown_2 = d.UInt16(self.data, 10)
        self.children_count = d.UInt16(self.data, 12)
        self.children = []
        self.padding = d.UInt16(self.data, 14)

        debug_print("Unknown_1:", self.unknown_1)
        debug_print("Unknown_2:", self.unknown_2)

        self.pointer = 16
        for i in range(self.children_count):
            self.children.append(ZOB_NPC_CE(self.data[self.pointer : self.pointer + 4]))
            debug_print(i, "-", self.children[len(self.children) - 1])
            self.pointer = self.pointer + 4


class ZOB_NPC_CE:
    def __init__(self, data):
        self.data = data
        self.npc = d.Decode(self.data)

    def save(self):
        return self.data

    def __str__(self):
        return str(self.npc)


class ZOB(ABC):
    """Abstract ZOB file. Use ZOB_NPC or ZOB_MOTYPE instead."""

    data: bytearray
    magic_string: str
    file_size: int
    unknown_1: int
    unknown_2: int
    children_count: int
    padding: int

    def __init__(self, data):
        self.data = data
        self.magic_string = self.data[:0x4].decode("ascii")
        self.file_size = d.UInt32(self.data, 0x4)
        self.unknown_1 = d.UInt16(self.data, 0x8)
        self.unknown_2 = d.UInt16(self.data, 0xA)
        self.children_count = d.UInt16(self.data, 0xC)
        self.padding = d.UInt16(self.data, 0xE)
        self.children = []

        debug_print("Unknown_1:", self.unknown_1)
        debug_print("Unknown_2:", self.unknown_2)

    @property
    def header_size(self) -> int:
        return 0xF

    def calculate_size(self):
        return len(self.data)

    def save(self) -> bytearray:
        buffer = bytearray(self.calculate_size())
        buffer[:4] = self.magic_string.encode("ascii")
        buffer = d.w_UInt32(buffer, 0x4, self.calculate_size())  # Size
        buffer = d.w_UInt16(buffer, 0x8, self.unknown_1)
        buffer = d.w_UInt16(buffer, 0xA, self.unknown_2)
        buffer = d.w_UInt16(buffer, 0xC, self.children_count)
        buffer = d.w_UInt16(buffer, 0xE, self.padding)

        for child in self.children:
            buffer = buffer + child.save()

        return buffer


class ZOB_NPC(ZOB):
    """npctype.zob file"""

    def __init__(self, data):
        super().__init__(data)

        self.pointer = 0x10
        for i in range(self.children_count):
            self.children.append(ZOB_NPC_CE(self.data[self.pointer : self.pointer + 4]))
            debug_print(i, "-", self.children[len(self.children) - 1])
            self.pointer = self.pointer + 4


class ZOB_MOTYPE(ZOB):
    """motype.zob file"""

    # TODO: implement this
    pass


class ZOB_CE:
    def __init__(self, data):
        self.data = data

        # temp code
        self._16_0 = d.UInt16(self.data, 0)
        self._s16_0 = d.SInt16(self.data, 0)

        self._16_2 = d.UInt16(self.data, 2)
        self._s16_2 = d.SInt16(self.data, 2)

        self._8_0 = d.UInt16(self.data, 0)
        self._s8_0 = d.SInt16(self.data, 0)

        self._8_1 = d.UInt8(self.data, 1)
        self._s8_1 = d.SInt8(self.data, 1)

    def __str__(self):
        return str(self._16_0) + " - " + str(self._s16_2)
