from .Utilities import *

import binascii

class FHM_AC6:

    def __init__(self) -> None:
        
        self.table_offset_entries = []
        self.table_entries = []

    class GYZ_OFFSET_ENTRY:

        def __init__(self) -> None:
            self.offset = 0
            self.size = 0

    class GYZ_ENTRY:

        def __init__(self) -> None:
            self.offset = 0
            self.size = 0

        def read(self, br):
            self.unk1 = br.readUInt()
            self.unk2 = br.readUInt()
            self.unk3 = br.readUInt()
            self.unk4 = br.readUInt()
            self.unk5 = br.readUInt()
            self.unk6 = br.readUInt()
            self.unk7 = br.readUInt()
            self.unk8 = br.readUInt()

            self.size = br.readUInt()
            self.offset = br.readUInt()

            self.unk9 = (br.readUByte(), br.readUByte(), br.readUByte(), br.readUByte())
            self.unk10 = br.readUInt()
            self.unk11 = br.readUInt()
            self.unk12 = br.readUInt()
            self.unk13 = br.readUInt()
            self.unk14 = br.readUInt()
            
    def read(self, br):

        header = br.bytesToString(br.readBytes(4)).replace("\0", "")
        br.readUInt()
        br.readUInt()
        br.readUInt()

        count = br.readUInt()

        self.read_gyz_offset_entry(br, count)

        self.read_gyz_entry(br, count)

        # Skip GYZ
        for i in range(len(self.table_entries)):

            br.seek(self.table_offset_entries[i].offset, 0)
            br.seek(self.table_offset_entries[i].size, 1)

        print(br.tell())
        
    def read_gyz_offset_entry(self, br, count):

        for i in range(count):
            table_offset_entry = FHM_AC6.GYZ_OFFSET_ENTRY()
            table_offset_entry.offset = br.readUInt()
            self.table_offset_entries.append(table_offset_entry)

        for i in range(len(self.table_offset_entries)):
            self.table_offset_entries[i].size = br.readUInt()

    def read_gyz_entry(self, br, count):

        for i in range(count):
            br.seek(self.table_offset_entries[i].offset, 0)
            table_entry = FHM_AC6.GYZ_ENTRY()
            table_entry.read(br)
            self.table_entries.append(table_entry)

    def read_unk1(self, br):

        header = br.tell()

        count1 = br.readUInt()
        str(binascii.hexlify(br.readBytes(4)), "ascii")
        count2 = br.readUInt() # count for hashs
        size1 = br.readUInt()
        br.readUInt()
        count3 = br.readUInt()
        offset1 = br.readUInt()
        size2 = br.readUInt()
        br.readUInt()
        br.readUInt()
        br.readUInt()
        br.readUInt()
        br.readUInt()
        hash_table_size = br.readUInt()

        for i in range(count2):
            str(binascii.hexlify(br.readBytes(4)), "ascii")

        br.seek(header + hash_table_size, 0)


