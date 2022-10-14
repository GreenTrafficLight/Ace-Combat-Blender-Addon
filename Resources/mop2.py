import binascii

from mathutils import *

class MOP2: # Animation Data

    def __init__(self) -> None:
        
        self.basepos_idx = -1
        self.kfm1_structs = []

    class HEADER:

        def __init__(self) -> None:
            
            self.sign = ""
            self.unk1 = 0
            self.unk2 = 0
            self.size = 0
            self.equals_to_size = 0
            self.kfm1_count = 0
            self.offset_to_kfm1_sizes = 0
            self.offset_to_kfm1_data_offsets = 0
            self.offset_to_kfm1_names_offsets = 0

        def read(self, br):

            self.sign = br.bytesToString(br.readBytes(4)).replace("\0", "")
            self.unk1 = br.readUShort()
            self.unk2 = br.readUShort()
            self.size = br.readUInt()
            self.equals_to_size = br.readUInt()
            self.kfm1_count = br.readUInt()
            self.offset_to_kfm1_sizes = br.readUInt()
            self.offset_to_kfm1_data_offsets = br.readUInt()
            self.offset_to_kfm1_names_offsets = br.readUInt()

    class FHM1_ENTRY:

        def __init__(self) -> None:
            self.offset = 0
            self.size = 0
            self.name_offset = ""

    class KFM1 : # Vertex morph data

        class SEQUENCE_HEADER:

            def __init__(self) -> None:
                
                self.unk = 0
                self.offsets_size = 0
                self.first_offset = 0
                self.unk2 = 0

            def read(self, br):
                
                self.unk = br.readUShort()
                self.offsets_size = br.readUShort()
                self.first_offset = br.readUShort()
                self.unk2 = br.readUShort()

        class SEQUENCE_BONE:

            def __init__(self) -> None:
                
                self.frames_offset = 0
                self.frames_count = 0
                self.offset = 0

            def read(self, br):
                
                self.frames_offset = br.readUShort()
                self.frames_count = br.readUShort()
                self.offset = br.readUShort()

        class SEQUENCE:

            def __init__(self) -> None:
                
                self.unknown = 0
                self.sequence_size = 0
                self.sequence_offset = 0

                self.header = None

                self.bones = []

            def read(self, br):
                
                self.unknown = br.readUShort()
                self.sequence_size = br.readUInt()
                self.sequence_offset = br.readUInt()

                self.header = MOP2.KFM1.SEQUENCE_HEADER()
                self.header.read(br)

        class BONE_INFO:

            def __init__(self) -> None:
                self.unk = []
                self.bone_idx = []
                self.unk2 = []          
                self.unk3 = []
                self.unk4 = []
                self.unk5 = []
                self.unk6 = []
                self.unk_zero = []

            def read(self, br):

                for i in range(3):
                    self.unk.append(br.readUShort())
                self.bone_idx = br.readUShort()
                self.unk2 = br.readUShort()                
                self.unk3 = br.readUShort()
                self.unk4 = br.readUShort()  
                self.unk5 = br.readUShort()
                self.unk6 = br.readUInt()
                for i in range(3):
                    self.unk_zero.append(br.readUInt())

        class HEADER:

            def __init__(self) -> None:
                
                self.sign = ""
                self.unk = 0
                self.unk2 = 0
                self.size = 0
                self.unk3 = 0
                self.bones_count = 0
                self.bones2_count = 0
                self.sequences_count = 0
                self.offset_to_bones = 0
                self.offset_to_sequences = 0
                self.offset_to_sequences_offsets = 0
                self.unk4 = 0
                self.offset_to_name = 0
                self.unk5 = 0
                self.unk6 = 0    
                self.unk7 = 0
                self.unk_zero2 = [] 


            def read(self, br):
                
                self.sign = br.bytesToString(br.readBytes(4)).replace("\0", "")
                self.unk = br.readUInt()
                self.unk2 = br.readUInt()
                self.size = br.readUInt()
                self.unk3 = br.readUShort()
                self.bones_count = br.readUShort()
                self.bones2_count = br.readUShort()
                self.sequences_count = br.readUShort()
                self.offset_to_bones = br.readUInt()
                self.offset_to_sequences = br.readUInt()
                self.offset_to_sequences_offsets = br.readUInt()
                self.unk4 = br.readUInt()
                self.offset_to_name = br.readUInt()
                self.unk5 = br.readUInt()
                self.unk6 = br.readUInt()    
                self.unk7 = br.readUInt()
                for i in range(2):
                    self.unk_zero2.append(br.readUInt())

        class STRUCT:

            def __init__(self) -> None:
                
                self.name = ""
                self.header = None
                self.bones = []
                self.bones2 = []
                self.sequences = []

            def read(self,br):
                
                pass

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

    def read(self, br):

        MOP2_position = br.tell()
        header = MOP2.HEADER()
        header.read(br)

        kfm1_entries = []

        for i in range(header.kfm1_count):

            kfm1_entry = MOP2.FHM1_ENTRY()
            br.seek(header.offset_to_kfm1_sizes + MOP2_position + 4 * i, 0)
            kfm1_entry.size = br.readUInt()
            br.seek(header.offset_to_kfm1_data_offsets + MOP2_position + 4 * i, 0)
            kfm1_entry.offset = br.readUInt()
            br.seek(header.offset_to_kfm1_names_offsets + MOP2_position + 4 * i, 0)
            kfm1_entry.name_offset = br.readUInt()

            kfm1_entries.append(kfm1_entry)
        
        for i in range(header.kfm1_count):
            kfm1_struct = MOP2.KFM1.STRUCT()
            
            br.seek(kfm1_entries[i].name_offset + MOP2_position)
            kfm1_struct.name = br.readString()
            if kfm1_struct.name == "basepose":
                self.basepos_idx = i
            self.kfm1_structs.append(kfm1_struct)

        for fi in range(header.kfm1_count):

            i = self.basepos_idx if fi == 0 else 0 if fi == self.basepos_idx else fi
            first_anim = i == 0

            br.seek(kfm1_entries[i].offset + MOP2_position)

            kfm1 = self.kfm1_structs[i]
            KFM1_position = br.tell()
            kfm1.header = MOP2.KFM1.HEADER()
            kfm1.header.read(br)

            br.seek(kfm1.header.offset_to_bones + KFM1_position)
            for b in range(kfm1.header.bones_count):
                b = MOP2.KFM1.BONE_INFO()
                
                b.read(br)
                kfm1.bones.append(b)

            for b in range(kfm1.header.bones2_count):
                b = MOP2.KFM1.BONE_INFO()
                
                b.read(br)
                kfm1.bones2.append(b)
    
            for k in range(kfm1.header.sequences_count):
                kfm1_sequence = MOP2.KFM1.SEQUENCE()
                
                br.seek(kfm1.header.offset_to_sequences + KFM1_position + k * 2)
                kfm1_sequence.unknown = br.readUShort()
                
                br.seek(kfm1.header.offset_to_sequences_offsets + KFM1_position + k * 8)
                kfm1_sequence.sequence_size = br.readUInt()
                kfm1_sequence.sequence_offset = br.readUInt()
                kfm1.sequences.append(kfm1_sequence)

            for k in range(kfm1.header.sequences_count):

                is_bones2 = len(kfm1.bones2) != 0 and k > 0

                f = kfm1.sequences[k]
                br.seek(kfm1.sequences[k].sequence_offset + KFM1_position)
                KFM1_SEQUENCE_position = br.tell()
                #print(br.tell())

                f.header = MOP2.KFM1.SEQUENCE_HEADER()
                f.header.read(br)

                first_offset = -1

                for b in range(kfm1.header.bones2_count if is_bones2 else kfm1.header.bones_count):
                    bone = MOP2.KFM1.SEQUENCE_BONE()
                    bone.read(br)
                
                    if bone.offset < first_offset:
                        first_offset = bone.offset

                    f.bones.append(bone)

                for j in range(len(f.bones)):
                     
                    br.seek(f.bones[j].offset + KFM1_SEQUENCE_position)

                    b = kfm1.bones2[j] if is_bones2 else kfm1.bones[j]

                    idx = b.bone_idx

                    frame_time = 16

                    is_quat = b.unk2 == 1031



            



