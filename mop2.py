import binascii

from unicodedata import name

from mathutils import *

class MOP2: # Animation Data

    class FHM1_ENTRY:

        def __init__(self) -> None:
            self.offset = 0
            self.size = 0
            self.name_offset = ""

    class KFM1 : # Vertex morph data

        class TRANSFORMATION_TABLE:

            def __init__(self) -> None:
                self.unk1 = 0
                self.index = 0
                self.offset = 0

            def read(self, br):

                self.unk1 = br.readUInt()
                self.index = br.readUShort()
                self.offset = br.readUShort()

        def __init__(self) -> None:
            
            self.name = ""

            self.translations = []
            self.quaternions = []

        def read(self, br):

            KFM1_position = br.tell()
            header = br.bytesToString(br.readBytes(4)).replace("\0", "")
            self.unk1 = br.readUInt()
            size1 = br.readUInt()
            KFM1_size = br.readUInt()
            self.unk2 = br.readUShort()
            count1 = br.readUShort() # 32 bytes each
            self.unk3 = br.readUShort()
            self.unk4 = br.readUShort()
            offset1 = br.readUInt() # offset for count1
            offset2 = br.readUInt()
            offset3 = br.readUInt()
            br.readBytes(4)
            name_offset = br.readUInt()

            br.readUShort()
            br.readUShort()

            br.seek(offset1 + KFM1_position, 0)
            for i in range(count1):
                str(binascii.hexlify(br.readBytes(4)), "ascii")
                br.readUByte()
                br.readUByte()
                br.readUByte() # mesh Index
                br.readUByte()
                br.readUByte()
                br.readUByte()
                br.readUByte()
                br.readUByte()
                br.readUShort()
                br.readUShort()
                br.readUShort()
                br.readUShort()

            br.seek(offset2 + KFM1_position, 0)
            br.readUShort()
            br.readUShort()
            
            br.seek(offset3 + KFM1_position, 0)
            size1 = br.readUInt() # size for offset 4
            offset4 = br.readUInt() # offset for transformation data ?
            size2 = br.readUInt() # size for offset 5
            offset5 = br.readUInt() # offset for animation Data ?
            
            br.seek(offset4 + KFM1_position, 0)
            transformation_tables = []
            transformation_tables_position = br.tell()
            str(binascii.hexlify(br.readBytes(4)), "ascii")
            transformations_offset = br.readUShort()
            br.readUShort() # Size of table and transformation
            
            for i in range(count1):
                transformation_table = MOP2.KFM1.TRANSFORMATION_TABLE()
                transformation_table.read(br)
                transformation_tables.append(transformation_table)

            for transformation_table in transformation_tables:

                br.seek(transformation_table.offset + transformation_tables_position, 0)
                if transformation_table.index % 2 == 0:
                    self.translations.append((br.readFloat(), br.readFloat(), br.readFloat()))
                else:
                    quaternion = (br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat())
                    self.quaternions.append(Quaternion((quaternion[3], quaternion[0], quaternion[1], quaternion[2])))

            br.seek(name_offset + KFM1_position, 0)
            self.name = br.readString()

    def __init__(self) -> None:
        
        self.kfm1_dict = {}

    def read(self, br):

        MOP2_position = br.tell() - 4
        self.unk1 = br.readUShort()
        self.unk2 = br.readUShort()
        
        mop2_size = br.readUInt()
        mop2_size2 = br.readUInt() # ?

        count = br.readUInt() # count ?

        kfm1_entries = []

        kfm1_sizes_offset = br.readUInt()
        kfm1_offsets_offset = br.readUInt()
        kfm1_names_offset = br.readUInt()

        for i in range(count):

            kfm1_entry = MOP2.FHM1_ENTRY()
            br.seek(kfm1_sizes_offset + MOP2_position + 4 * i, 0)
            kfm1_entry.size = br.readUInt()
            br.seek(kfm1_offsets_offset + MOP2_position + 4 * i, 0)
            kfm1_entry.offset = br.readUInt()
            br.seek(kfm1_names_offset + MOP2_position + 4 * i, 0)
            kfm1_entry.name_offset = br.readUInt()

            kfm1_entries.append(kfm1_entry)

        for kfm1_entry in kfm1_entries:

            kfm1 = MOP2.KFM1()

            br.seek(kfm1_entry.name_offset + MOP2_position, 0)
            kfm1_name = br.readString()
            if kfm1_name == "basepose":
                self.kfm1_dict[kfm1_name] = kfm1
                br.seek(kfm1_entry.offset + MOP2_position, 0)
                kfm1.read(br)


