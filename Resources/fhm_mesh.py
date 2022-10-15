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
        ndxr_offset = -1
        for j in range(len(fhm_file.m_chunks)):
            sign = fhm_file.m_chunks[j].type
            if sign == "MNT":
                mnt_count += 1
            elif sign == "MOP2":
                mop2_count += 1
            elif (sign == "NDXR" or sign == "NDP3") and ndxr_offset == -1:
                ndxr_offset = j
            
        lods_count = 0
        for j in range(ndxr_offset, len(fhm_file.m_chunks)):

            sign = fhm_file.m_chunks[j].type
            if sign == "NDXR" or sign == 0 or sign == "NDP3":
                lods_count += 1
            else:
                break

        if lods_count > 0:

            signs = ["MNT", "MOP2", "NDXR NDP3"]

            special_mnt = mnt_count <= 2
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
                        self.mnts.append(mnt)
                    elif i == 1 and sign == "MOP2":
                        mop2 = MOP2()
                        mop2.read(br)
                        self.mop2s.append(mop2)
                    elif i == 2 and (sign == "NDXR" or sign == "NDP3"):
                        nd = ND()
                        nd.read(br)
                        self.nds.append(nd)

