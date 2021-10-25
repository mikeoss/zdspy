from abc import ABCMeta, abstractclassmethod, abstractmethod
from collections import defaultdict
import struct

from ndspy import lz10, narc
from ..zdspy import bmg, zmb

# TODO: maybe move these out of zdspy and into their own module?


class Location:
    """A generic 'location' in the game that contains an item."""

    def __init__(self, file_path: list[str]):
        self.file_path = file_path

    @abstractmethod
    def set_location(self, value: int):
        pass

    @abstractclassmethod
    def save_all():
        pass


class BMG_Location(Location):
    _filename_to_bmg_mapping: dict[bmg.BMG, str] = {}

    def __init__(self, instruction_index: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instruction_index = instruction_index
        self.bmg_file = bmg.BMG.fromFile(self.file_path)
        BMG_Location._filename_to_bmg_mapping[self.bmg_file] = self.file_path

    def set_location(self, value: int):
        self.bmg_file.instructions[self.instruction_index] = (
            self.bmg_file.instructions[self.instruction_index][:4]
            + struct.pack("<B", value)
            + self.bmg_file.instructions[self.instruction_index][5:]
        )

    @classmethod
    def save_all(cls):
        for bmg_file, filename in BMG_Location._filename_to_bmg_mapping.items():
            bmg_file.saveToFile(filename)


class ZMB_MPOB_Location(Location):
    # maps filenames objects to ZMB objects
    _zmb_filename_mapping: dict[zmb.ZMB, str] = {}

    # maps NARC file objects to filenames
    _narc_filename_mapping: dict[narc.NARC, str] = {}

    # mapping between ZMB file names and their parent NARC files
    _narc_to_zmb_mapping: dict[narc.NARC, list[str]] = defaultdict(list)

    def __init__(self, child_index: int, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.child_index = child_index
        self.zmb_file = None

        # check if this zmb file is already open first
        for filename, zmb_file in ZMB_MPOB_Location._zmb_filename_mapping.items():
            if filename == self._zmb_filepath:
                self.zmb_file = zmb_file

        if self.zmb_file is None:
            with open(self._narc_filepath, "rb") as narc_fd:
                narc_file = narc.NARC(lz10.decompress(narc_fd.read()))
                ZMB_MPOB_Location._narc_filename_mapping[
                    narc_file
                ] = self._narc_filepath
                self.zmb_file = zmb.ZMB(narc_file.getFileByName(self._zmb_filepath))
                ZMB_MPOB_Location._narc_to_zmb_mapping[narc_file].append(self._zmb_filepath)
                ZMB_MPOB_Location._zmb_filename_mapping[self._zmb_filepath] = self.zmb_file

    def set_location(self, value: int):
        zmb_child_element: zmb.ZMB_MPOB_CE = self.zmb_file.get_child('MPOB').children[self.child_index]
        zmb_child_element.item_id = value
        ZMB_MPOB_Location._zmb_filename_mapping[self._zmb_filepath] = self.zmb_file

    @property
    def _narc_filepath(self):
        """The filepath of the NARC archive (ending with '.bin' extension) containing this ZMB file."""
        path: list[str] = []
        for part in self.file_path.split("/"):
            path.append(part)
            if "." in part:
                return "/".join(path)

    @property
    def _zmb_filepath(self):
        """The filepath of the ZMB file within its parent NARC archive."""
        index: int
        part: str
        for index, part in enumerate(self.file_path.split("/")):
            if "." in part:
                return "/".join(self.file_path.split("/")[index + 1 :])

    @classmethod
    def save_all(cls):
        for narc_file, zmb_filenames in ZMB_MPOB_Location._narc_to_zmb_mapping.items():
            print(zmb_filenames)
            for zmb_filename in zmb_filenames:
                print(zmb_filename)
                print(ZMB_MPOB_Location._zmb_filename_mapping)
                narc_file.setFileByName(
                    zmb_filename,
                    ZMB_MPOB_Location._zmb_filename_mapping[zmb_filename].save(),
                )
            lz10.compressToFile(
                (narc_file.save()),
                ZMB_MPOB_Location._narc_filename_mapping[narc_file],
            )
