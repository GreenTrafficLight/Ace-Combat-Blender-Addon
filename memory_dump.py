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

    def read(self, br, file_size, mnt_debug):

        br.endian = ">"
        
        addr_off = 0
        br.seek(0x0A, 0)
        count = br.readUShort()
        if count > 0:
            br.seek(0x5C, 0)
            addr_off = br.readUInt() - (48 + (count * 0x30))
        br.seek(0, 0)

        br.endian = "<"

        if mnt_debug:

            self.mnt_list = [(None, 0x3) for _ in range(11)]

        subheader = ""

        while br.tell() < file_size:

            subheader += br.bytesToString(br.readBytes(1)).replace("\0", "")

            if "NDP3" in subheader:

                save_addr = br.tell() - 4

                ndp3 = NDXR()
                ndp3.read(br, ">", True, addr_off)

                br.seek(save_addr + ndp3.size, 0)

                self.nd_list.append((ndp3, 0x1))

                subheader = ""
            
            elif "NDXR" in subheader:

                print(br.tell() - 4)

                save_addr = br.tell() - 4

                ndxr = NDXR()
                ndxr.read(br, ">", True, addr_off)

                br.seek(save_addr + ndxr.size, 0)

                self.nd_list.append((ndxr, 0x1))

                subheader = ""      

            elif "MNT" in subheader:

                br.seek(1, 1)

                save_addr = br.tell() - 4

                mnt = MNT()
                mnt.read(br)

                br.seek(save_addr + mnt.size, 0)

                if mnt_debug:

                    if "_body" in mnt.names[0]:
                        self.mnt_list[0] = (mnt, 0x3)

                    elif "_c1" in mnt.names[0]:
                        self.mnt_list[1] = (mnt, 0x3)

                    elif "_c2" in mnt.names[0]:
                        self.mnt_list[2] = (mnt, 0x3)
                    
                    elif "BINE_BONE" in mnt.names[0]:
                        
                        if self.mnt_list[3] == (None, 0x3):
                            self.mnt_list[3] = (mnt, 0x3)

                        elif self.mnt_list[9] == (None, 0x3):
                            self.mnt_list[9] = (mnt, 0x3)
                    
                    elif "_gear" in mnt.names[0]:
                        self.mnt_list[4] = (mnt, 0x3)

                    elif "_psel" in mnt.names[0]:
                        self.mnt_list[5] = (mnt, 0x3)

                    elif "_shbody" in mnt.names[0]:
                        self.mnt_list[6] = (mnt, 0x3)

                    elif "_shc1" in mnt.names[0]:
                        self.mnt_list[7] = (mnt, 0x3)

                    elif "_shc2" in mnt.names[0]:
                        self.mnt_list[8] = (mnt, 0x3)

                    elif "_shgear" in mnt.names[0]:
                        self.mnt_list[10] = (mnt, 0x3)

                    elif "_nozl" in mnt.names[0]:
                        self.mnt_list[3] = (mnt, 0x3)

                    elif "_shnozl" in mnt.names[0]:
                        self.mnt_list[9] = (mnt, 0x3)

                    else:
                        self.mnt_list.append((mnt, 0x3))

                else:
                    self.mnt_list.append((mnt, 0x3))

                subheader = ""

            elif "MOP2" in subheader:

                save_addr = br.tell() - 4

                mop2 = MOP2()
                mop2.read(br)

                br.seek(save_addr + mop2.size, 0)

                self.mop2_list.append((mop2, 0x4))

                subheader = ""
                
            elif "MATE" in subheader:

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
      
        for i in range(len(self.mnt_list)):

            if self.mnt_list[i][0] == None:

                self.nd_list.insert(i, (None, 0x1))
                self.mop2_list.insert(i, (None, 0x4))
