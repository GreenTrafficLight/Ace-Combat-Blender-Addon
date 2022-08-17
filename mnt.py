from mathutils import *

from .Utilities import *

class NDXR:
    def __init__(self):

        pass

    def read(self, br):

        MNT_position = br.tell() - 4
        br.readUInt()
        MNT_size = br.readUInt()