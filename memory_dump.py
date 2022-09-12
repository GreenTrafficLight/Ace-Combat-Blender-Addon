from .Utilities import *

from .ndxr import *
from .mnt import *
from .mop2 import *
from .colh import *

class MEMORY_DUMP:

    def __init__(self) -> None:

        self.nd_list = []
        self.mnt_list = []
        self.mop2_list = []

    def read(self, br, file_size):

        br.endian = ">"
        
        addr_off = 0
        br.seek(0x0A, 0)
        count = br.readUShort()
        if count > 0:
            br.seek(0x5C, 0)
            addr_off = br.readUInt() - (48 + (count * 0x30))
        br.seek(0, 0)

        br.endian = "<"

        subheader = ""

        while br.tell() < file_size:

            subheader += br.bytesToString(br.readBytes(1)).replace("\0", "")

            if subheader == "NDP3":

                save_addr = br.tell() - 4

                ndp3 = NDXR()
                ndp3.read(br, ">", True, addr_off)

                br.seek(save_addr + ndp3.size, 0)

                self.nd_list.append(ndp3)

                subheader = ""
            
            elif subheader == "NDXR":

                print(br.tell() - 4)

                save_addr = br.tell() - 4

                ndxr = NDXR()
                ndxr.read(br, ">", True, addr_off)

                br.seek(save_addr + ndxr.size, 0)

                self.nd_list.append(ndxr)

                subheader = ""      

            elif subheader == "MNT":

                br.seek(1, 1)

                save_addr = br.tell() - 4

                mnt = MNT()
                mnt.read(br)

                br.seek(save_addr + mnt.size, 0)

                self.mnt_list.append(mnt)

                subheader = ""

            elif subheader == "MOP2":

                save_addr = br.tell() - 4

                mop2 = MOP2()
                mop2.read(br)

                br.seek(save_addr + mop2.size, 0)

                self.mop2_list.append(mop2)

                subheader = ""
                

            elif subheader == "MATE":

                break

                go_to_colh = data.find(b"\x43\x4F\x4C\x48") # TEST
                br.seek(go_to_colh)

                subheader = ""

            elif subheader == "COLH":

                save_addr = br.tell() - 4

                colh = COLH()
                colh.read(br)

                br.seek(save_addr + colh.size, 0)

                # TEST
                br.seek(1024, 1)
                br.seek(48, 1)

                subheader = ""
      
