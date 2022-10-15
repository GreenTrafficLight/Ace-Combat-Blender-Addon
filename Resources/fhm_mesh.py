from .fhm_file import *
from .mnt import *
from .mop2 import *
from .ndxr import *

class FHM_MESH:

    def __init__(self) -> None:
        
        self.mnts = []
        self.mop2s = []
        self.nds = []

    def load(self, br):

        fhm_file = FHM()
        fhm_file.open(br)

        mnt_count = 0
        mop2_count = 0
        lods_count = 0
        total_lods_count = 0
        ndxr_offset = -1

        lods_offsets = []
        
        for j in range(len(fhm_file.m_chunks)):
            sign = fhm_file.m_chunks[j].type
            if sign == 0x4d4e5400: # "MNT"
                mnt_count += 1
            elif sign == 0x4d4f5032: # "MOP2"
                mop2_count += 1
            elif (sign == 0x4e445852 or sign == 0x4e445033): # ND
                lods_count += 1
                total_lods_count += 1
                if ndxr_offset == -1:
                    ndxr_offset = j
            elif sign == 0x3 or sign == 0x3000000:
                pass
            else:
                if ndxr_offset != -1:
                    lods_offsets.append((ndxr_offset, lods_count))
                    lods_count = 0
                    ndxr_offset = -1

        print("test")

        if len(lods_offsets) > 0:

            self.mnts = [None for _ in range(total_lods_count)]
            self.mop2s = [None for _ in range(total_lods_count)]
            self.nds = [None for _ in range(total_lods_count)]

            special_mnt = mnt_count <= 2
            """
            if (special_mnt and mnt_count > 0):
                for j in range(2):
                    idx = 0
                    for i in range(len(fhm_file.m_chunks)):
                        if fhm_file.m_chunks[i].type == signs[j]:

                            idx += 1
                            _from = idx * lods_count/mnt_count
                            to = _from + lods_count/mnt_count
                            if j == 0:

                                mnt = MNT()
                                for i in range(_from + 1, to):
                                    pass
                            
                            else:
                                
                                mop2 = MOP2()
                                for i in range(_from + 1, to):
                                    pass
            """

            """

            offsets = [lods_count, lods_count * 2, 0]
            
            for i in range(2 if special_mnt else 0, 3):

                for j in range(lods_count):

                    idx = ndxr_offset + offsets[i] + j 
                    sign = fhm_file.m_chunks[idx].type
                    size = fhm_file.m_chunks[idx].size

                    br.seek(fhm_file.m_chunks[idx].offset, 0)

                    if i == 0 and sign == "MNT":
                        mnt = MNT()
                        mnt.read(br)
                        self.mnts[j] = mnt
                    elif i == 1 and sign == "MOP2":
                        mop2 = MOP2()
                        mop2.read(br)
                        self.mop2s[j] = mop2
                    elif i == 2 and (sign == "NDXR" or sign == "NDP3"):
                        nd = ND()
                        nd.read(br)
                        self.nds[j] = nd
            """

            k = 0

            for i in range(len(lods_offsets)):

                lod_offset = lods_offsets[i]

                if i != 0:
                    k += lods_offsets[i - 1][1]

                for j in range(2 if special_mnt else 0, 3):

                    idx = lod_offset[0]

                    l = 0

                    while True:

                        if i != (len(lods_offsets) - 1) and idx >= lods_offsets[i + 1][0]:
                        
                            break

                        elif i == (len(lods_offsets) - 1) and idx >= len(fhm_file.m_chunks):

                            break
                        
                        sign = fhm_file.m_chunks[idx].type
                        size = fhm_file.m_chunks[idx].size

                        br.seek(fhm_file.m_chunks[idx].offset, 0)

                        if j == 0 and sign == 0x4d4e5400:
                            mnt = MNT()
                            mnt.read(br)
                            self.mnts[k + l] = mnt
                            l += 1
                        elif j == 1 and sign == 0x4d4f5032:
                            mop2 = MOP2()
                            mop2.read(br, self.mnts[k + l])
                            self.mop2s[k + l] = mop2
                            l += 1
                        elif j == 2 and (sign == 0x4e445852 or sign == 0x4e445033):
                            nd = ND()
                            nd.read(br)
                            self.nds[k + l] = nd
                            l += 1

                        idx += 1


            print("test")