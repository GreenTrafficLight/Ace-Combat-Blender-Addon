class MOP2:

    class FHM1_ENTRY:

        def __init__(self) -> None:
            self.offset = 0
            self.size = 0
            self.name_offset = ""

    class KFM1 :

        def __init__(self) -> None:
            
            self.name = ""

        def read(self, br):

            KFM1_position = br.tell() - 4
            br.readUInt()

    def __init__(self) -> None:
        
        self.kfm1_list = []

    def read(self, br):

        MOP2_position = br.tell() - 4
        br.readUShort()
        br.readUShort()
        
        mop2_size = br.readUInt()
        mop2_size2 = br.readUInt() # ?

        count = br.readUInt() # count ?

        kfm1_entries = []

        kfm1_sizes_offset = br.readUInt()
        kfm1_offsets_offset = br.readUInt()
        kfm1_names_offset = br.readUInt()

        for i in range(count):

            kfm1_entry = MOP2.FHM1_ENTRY()
            br.seek(kfm1_sizes_offset + MOP2_position + 4 * i, 0)
            kfm1_entry.size = br.readUInt()
            br.seek(kfm1_offsets_offset + MOP2_position + 4 * i, 0)
            kfm1_entry.offset = br.readUInt()
            br.seek(kfm1_names_offset + MOP2_position + 4 * i, 0)
            kfm1_entry.name_offset = br.readUInt()

            kfm1_entries.append(kfm1_entry)

        for kfm1_entry in kfm1_entries:

            kfm1 = MOP2.KFM1()

            br.seek(kfm1_entry.name_offset + MOP2_position, 0)
            kfm1.name = br.readString()
            br.seek(kfm1_entry.offset + MOP2_position, 0)

            self.kfm1_list.append(kfm1)


