from .Utilities import *

from .ndxr import *

class FHM:

    def __init__(self) -> None:
        
        self.table_offset_entries = []
        self.table_entries = []

    def read(self, br):

        header = br.bytesToString(br.readBytes(4)).replace("\0", "")
        br.readUInt()
        br.readUInt()
        br.readUInt()

        # + 0x30
        table_size = br.readUInt()
        file_size = br.readUInt()
        #

        br.readUInt()
        br.readUInt()
        br.readUInt()
        br.readUInt()
        br.readUInt()
        br.readUInt()

        count = br.readUInt()

        self.read_table_offset_entry(br, count)

        self.read_table_entry(br, count)

        for table_entry in self.table_entries:

            br.seek(table_entry.offset + 0x30, 0)

            header = br.bytesToString(br.readBytes(4)).replace("\0", "")

            if header == "NDXR":

                ndxr = NDXR()
                ndxr.read()



    def read_table_offset_entry(self, br, count):

        for i in range(count):
            table_offset_entry = FHM.TABLE_OFFSET_ENTRY()
            self.table_offset_entries.append(table_offset_entry.read(br))

    def read_table_entry(self, br, count):

        for i in range(count):
            br.seek(self.table_offset_entries[i] + 0x30, 0)
            table_entry = FHM.TABLE_ENTRY()
            self.tablet_entries.append(table_entry.read(br))

    class TABLE_OFFSET_ENTRY:

        def __init__(self) -> None:
            self.offset = 0

        def read(self, br):

            br.readUInt()
            self.offset = br.readUInt()

    class TABLE_ENTRY:

        def __init__(self) -> None:
            self.offset = 0
            self.size = 0

        def read(self, br):
            br.readUShort()
            br.readUShort()
            br.readUInt()
            self.offset = br.readUInt()
            self.size = br.readUInt()
    


