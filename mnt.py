from mathutils import *

from .Utilities import *

import binascii

class MNT: # Armature Data

    def __init__(self):

        self.size = 0

        self.unk1 = 0

        self.hashes = []
        self.hash_indices = []
        self.parent_indices = []
        self.nodes = []
        self.names = []

    class NODE :

        def __init__(self) -> None:
            
            self.index = 0
            self.child_index = 0
            self.sibling_index = 0
            self.parent_index = 0
            self.hash = ""

        def read(self, br):

            self.index = br.readShort()  # Index
            self.child_index = br.readShort()  # Child index ?
            self.sibling_index = br.readShort()  # Sibling index ?
            self.parent_index = br.readShort()  # Parent index
            self.hash = str(binascii.hexlify(br.readBytes(4)), "ascii") # Hash
            br.readBytes(8) # ???

    def read(self, br):

        MNT_position = br.tell() - 4
        self.unk1 = br.readUInt()
        self.size = br.readUInt()

        count = br.readUShort()

        self.unk1 = br.readUShort()
        self.unk2 = br.readUInt()
        self.unk3 = str(binascii.hexlify(br.readBytes(4)), "ascii")

        hashes_offset = br.readUInt()
        hash_indices_offset = br.readUInt()
        parent_indices_offset = br.readUInt()
        nodes_offset = br.readUInt()
        unk_offset = br.readUInt()
        
        names_offset = br.readUInt()

        # Hashes
        br.seek(hashes_offset + MNT_position)
        for i in range(count):
            self.hashes.append(str(binascii.hexlify(br.readBytes(4)), "ascii")) 

        # Hash indices
        br.seek(hash_indices_offset + MNT_position)
        for i in range(count):
            self.hash_indices.append(br.readShort())

        # Parent indices
        br.seek(parent_indices_offset + MNT_position)
        for i in range(count):
            self.parent_indices.append(br.readShort())

        # Nodes
        br.seek(nodes_offset + MNT_position)
        for i in range(count):
            node = MNT.NODE()
            node.read(br)
            self.nodes.append(node)

        # Zeros ?
        br.seek(unk_offset + MNT_position)
        for i in range(count):
            br.readUInt()

        # Names
        br.seek(names_offset + MNT_position)
        for i in range(count):
            self.names.append(br.readString())

    