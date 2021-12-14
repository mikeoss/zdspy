from abc import ABC, abstractmethod, abstractproperty

from . import dataio as d
from .helpers import debug_print


class IByteOrderMark:
    BYTE_ORDER_MARK_BIG_ENDIAN: str = "feff"
    BYTE_ORDER_MARK_LITTLE_ENDIAN: str = "fffe"
    byte_order_mark_string: str = "feff"

    def is_big_endian(self) -> bool:
        return self.byte_order_mark_string == self.BYTE_ORDER_MARK_BIG_ENDIAN

    def is_little_endian(self) -> bool:
        return not self.is_big_endian()


class ZDS_GenericElementHeaderIDO(ABC):
    data: bytearray
    identification: str

    def __init__(self, data):
        self.data = data
        self.identification = d.Decode(data[:4])
        # debug_print("Loading Element: " + self.identification)
        self.init()

    @abstractmethod
    def init(self):
        pass

    @abstractproperty
    def header_size(self) -> int:
        return 4


class ZDS_GenericElementHeaderRaw(ABC):
    data: bytearray
    identification: str
    size: int = 0

    def __init__(self, data):
        self.data = data
        self.identification = d.Decode(data[:4])
        # debug_print("Loading Element: " + self.identification)
        self.size = d.UInt32(data, 4)
        self.init()

    @abstractmethod
    def init(self):
        pass

    @abstractproperty
    def header_size(self) -> int:
        return 8


class ZDS_GenericElementHeaderRawNR(ABC):
    data: bytearray
    identification: str
    size: int = 0

    def __init__(self, data):
        self.data = data
        self.identification = data[:4].decode()
        # debug_print("Loading Element: " + self.identification)
        self.size = d.UInt32(data, 4)
        self.init()

    @abstractmethod
    def init(self):
        pass

    @abstractproperty
    def header_size(self) -> int:
        return 8


class ZDS_GenericElementHeader(ABC):
    data: bytearray
    identification: str
    size: int = 0
    children_count: int = 0
    children: list = []
    padding: int = 0
    offset: int = 0

    def __init__(self, data: bytearray):
        self.data = data
        self.identification = d.Decode(data[:4])
        # debug_print("Loading Element: " + self.identification)
        self.size = d.UInt32(data, 4)
        self.children_count = d.UInt16(data, 8)
        self.children = []
        self.padding = d.UInt16(data, 10)
        self.offset = self.header_size
        if not self.padding == 65535:
            debug_print("Padding with NON 0xFFFF Value: " + str(self.padding))
        self.init()

    @abstractmethod
    def init(self):
        pass

    @abstractproperty
    def header_size(self) -> int:
        return 12


class ZDS_GenericFileHeader(ABC, IByteOrderMark):  # TODO
    data: bytearray
    identification: str
    size: int = 0
    children_count: int = 0
    children: list = []
    padding: int = 0
    offset: int = 0
    _header_size: int = 16

    def __init__(self, data):
        self.data = data
        self.identification = data[:4].decode()
        # debug_print("Loading Element: " + self.identification)
        self.byte_order_mark_string = str(data[4:6].hex())
        if self.byte_order_mark_string == "feff":  # FEFF
            debug_print("Big Endian")
        elif self.byte_order_mark_string == "fffe":  # FFFE
            debug_print("Little Endian")
        else:
            debug_print("BOM is wrong!")
        self.unknwn1 = d.UInt16(data, 6)
        debug_print("Unknwn1 (0x06): " + str(self.unknwn1))
        self.children = []
        self.size = d.UInt32(data, 8)

        self.header_size = d.UInt16(data, 12)
        if not (self.header_size == 16):
            debug_print("Header Size not 16 !!!")

        self.children_count = d.UInt16(data, 14)

        self.offset = 16
        self.init()

    @abstractmethod
    def init(self):
        pass

    @property
    def header_size(self) -> int:
        return self._header_size

    @header_size.setter
    def set_header_size(self, value: int):
        self._header_size = value


# Programm Related:
class NDS_GenericTempContainer(ZDS_GenericElementHeaderRaw):
    def init(self):
        self.size2 = d.UInt32(self.data, 8)  # Might be unused in some cases.

    @property
    def header_size(self) -> int:
        return 20


class NDS_GenericTempContainerNR(ZDS_GenericElementHeaderRawNR):
    def init(self):
        self.size2 = d.UInt32(self.data, 8)  # Might be unused in some cases.

    @property
    def header_size(self) -> int:
        return 20
