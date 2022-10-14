from mathutils import *

from ..Utilities import *

import binascii

class MNT: # Armature Data

    def __init__(self):

        self.header = None

        self.size = 0

        self.unk1 = 0

        self.hashes = []
        self.hash_indices = []
        self.parent_indices = []
        self.nodes = []
        self.names = []

    class HEADER:

        def __init__(self) -> None:
            self.sign = ""
            self.unk1 = 0
            self.chunk_size = 0
            self.bones_count = 0
            self.unk2 = 0
            self.unk3 = 0    
            self.unknown_trash = []
            self.hashes_offset = 0
            self.hash_indices_offset = 0
            self.offset_to_parents = 0
            self.offset_to_bones = 0
            self.unk_offset = 0
            self.offset_to_bones_names = 0

        def read(self, br):
            
            self.sign = br.bytesToString(br.readBytes(4)).replace("\0", "")
            self.unk1 = br.readUInt()
            self.chunk_size = br.readUInt()
            self.bones_count = br.readUShort()
            self.unk2 = br.readUShort()
            self.unk3 = br.readUInt()
            for i in range(2):
                self.unknown_trash.append(br.readUShort())
            self.hashes_offset = br.readUInt()
            self.hash_indices_offset = br.readUInt()
            self.offset_to_parents = br.readUInt()
            self.offset_to_bones = br.readUInt()
            self.unk_offset = br.readUInt()
            self.offset_to_bones_names = br.readUInt()

    class MNT_BONE :

        def __init__(self) -> None:
            
            self.index = 0
            self.child_index = 0
            self.sibling_index = 0
            self.parent_index = 0
            self.hash = ""
            self.unknown_zero = 0

        def read(self, br):

            print(br.tell())
            self.index = br.readShort()  # Index
            self.child_index = br.readShort()  # Child index ?
            self.sibling_index = br.readShort()  # Sibling index ?
            self.parent_index = br.readShort()  # Parent index
            self.hash = str(binascii.hexlify(br.readBytes(8)), "ascii") # Hash
            self.unknown_zero = br.readUInt()

    def read(self, br):

        MNT_position = br.tell()
        self.header = MNT.HEADER()
        self.header.read(br)

        # Hashes
        br.seek(self.header.hashes_offset + MNT_position)
        for i in range(self.header.bones_count):
            self.hashes.append(str(binascii.hexlify(br.readBytes(4)), "ascii")) 

        # Hash indices
        br.seek(self.header.hash_indices_offset + MNT_position)
        for i in range(self.header.bones_count):
            self.hash_indices.append(br.readShort())

        # Parent indices
        br.seek(self.header.offset_to_parents + MNT_position)
        for i in range(self.header.bones_count):
            self.parent_indices.append(br.readShort())

        # Nodes
        br.seek(self.header.offset_to_bones + MNT_position)
        for i in range(self.header.bones_count):
            bone = MNT.MNT_BONE()
            bone.read(br)
            self.nodes.append(bone)

        # Zeros ?
        br.seek(self.header.unk_offset + MNT_position)
        for i in range(self.header.bones_count):
            br.readUInt()

        # Names
        br.seek(self.header.offset_to_bones_names + MNT_position)
        for i in range(self.header.bones_count):
            self.names.append(br.readString())

    