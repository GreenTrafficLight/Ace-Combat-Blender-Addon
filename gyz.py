from mathutils import *

from .Utilities import *

import binascii

class GYZ: # Animation Data ?

    def __init__(self):

        self.size = 0

        self.unk1 = 0
        self.unk2 = 0

    def read(self, br):

        GYZ_position = br.tell() - 4
        self.unk1 = br.readUShort()
        self.unk2 = br.readUShort()
        self.size = br.readUInt()

    