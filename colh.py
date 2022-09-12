from .Utilities import *

class COLH:

    def __init__(self):

        self.size = 0

    def read(self, br):

        COLH_position = br.tell() - 4
        self.size = br.readUInt()