from mathutils import *

from ..Utilities import *

class WPDC:

    def __init__(self):

        self.header = None

    class HEADER:

        def __init__(self) -> None:
            self.sign = ""
            self.version = ""
            self.unknown = 0
            self.unknown2 = 0
            self.unknown3 = 0
            self.width = 0
            self.height = 0
            self.zero = 0

        def read(self, br):
            
            self.sign = br.bytesToString(br.readBytes(4)).replace("\0", "")
            self.version = br.bytesToString(br.readBytes(4)).replace("\0", "")
            self.unknown = br.readUInt()
            self.unknown2 = br.readUInt()
            self.unknown3 = br.readUInt()
            self.width = br.readFloat()
            self.height = br.readFloat()
            self.zero = br.readUInt()

    def read(self, br):

        WPDC_POSITION = br.tell()
        header = WPDC.HEADER()
        header.read(br)
        offsets = []
        for i in range(16 * 16):
            offsets.append(br.readUInt())
        
