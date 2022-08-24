from re import sub
from .Utilities import *

from .ndxr import *
from .mnt import *
from .mop2 import *

class FHM:

    def __init__(self) -> None:
        
        self.table_offset_entries = []
        self.table_entries = []

        self.ndxr_list = []
        self.mnt_list = []
        self.mop2_list = []

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

        index = 0

        for table_entry in self.table_entries:

            if table_entry.size != 0:

                br.seek(table_entry.offset + 0x30, 0)

                subheader = br.bytesToString(br.readBytes(4)).replace("\0", "")

                if subheader == "NDXR":

                    print(str(index) + " " + subheader + " : " + str(br.tell()))

                    ndxr = NDXR()
                    ndxr.read(br)

                    self.ndxr_list.append(ndxr)

                elif subheader == "MNT":

                    print(str(index) + " " + subheader + " : " + str(br.tell()))

                    mnt = MNT()
                    mnt.read(br)

                    self.mnt_list.append(mnt)

                elif subheader == "MOP2":

                    print(str(index) + " " + subheader + " : " + str(br.tell()))

                    mop2 = MOP2()
                    mop2.read(br)

                    self.mop2_list.append(mop2)

                elif subheader == "MATE":

                    print(str(index) + " " + subheader + " : " + str(br.tell()))

                elif subheader == "COLH":

                   print(str(index) + " " + subheader + " : " + str(br.tell()))

                else :
                    
                    br.seek(-4, 1)

                    print(str(index) + " " + str(br.tell()))

            index += 1

    def read_table_offset_entry(self, br, count):

        for i in range(count):
            table_offset_entry = FHM.TABLE_OFFSET_ENTRY()
            table_offset_entry.read(br)
            self.table_offset_entries.append(table_offset_entry)

    def read_table_entry(self, br, count):

        for i in range(count):
            br.seek(self.table_offset_entries[i].offset + 0x30, 0)
            table_entry = FHM.TABLE_ENTRY()
            table_entry.read(br)
            self.table_entries.append(table_entry)

    class TABLE_OFFSET_ENTRY:

        def __init__(self) -> None:
            self.offset = 0

        def read(self, br):

            self.unk1 = br.readUInt()
            self.offset = br.readUInt()

    class TABLE_ENTRY:

        def __init__(self) -> None:
            self.offset = 0
            self.size = 0

        def read(self, br):
            self.unk1 = br.readUShort()
            self.unk2 = br.readUShort()
            self.unk3 = br.readUInt()
            self.offset = br.readUInt()
            self.size = br.readUInt()
    


