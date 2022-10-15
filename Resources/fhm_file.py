from ..Utilities import *

class FHM:

    def __init__(self) -> None:
        
        self.m_chunks = []

    class HEADER:

        def __init__(self) -> None:

            self.sign = ""
            self.byte_order_20101010 = 0
            self.timestamp = 0
            self.unknown_struct_count = 0

            self.unk = 0
            self.size = 0
            self.unk2 = 0
            self.unk3 = 0
            self.unk4 = 0
            self.unk5 = 0
            self.unknown_pot = 0
            self.unknown_pot2 = 0   

        def read(self, br):

            self.sign = br.bytesToString(br.readBytes(4)).replace("\0", "")
            self.byte_order_20101010 = br.readUInt()
            self.timestamp = br.readUInt()
            self.unknown_struct_count = br.readUInt()

            self.unk = br.readUInt()
            self.size = br.readUInt()
            self.unk2 = br.readUInt()
            self.unk3 = br.readUInt()
            self.unk4 = br.readUInt()
            self.unk5 = br.readUInt()
            self.unknown_pot = br.readUInt() 
            self.unknown_pot2 = br.readUInt()

    class CHUNK:

        def __init__(self) -> None:
            self.type = ""
            self.offset = 0
            self.size = 0

    def open(self, br):

        header = FHM.HEADER()
        header.read(br)

        self.read_chunks_info(br, 48)

        print(br.tell())

    class CHUNK_INFO:

        def __init__(self) -> None:
            self.unk1 = 0
            self.unk2 = 0
            self.unk_pot = 0
            self.offset = 0
            self.size = 0

        def read(self, br, offset):
            br.seek(offset, 0)
            self.unk1 = br.readUShort()
            self.unk2 = br.readUShort()
            self.unk_pot = br.readUInt()
            self.offset = br.readUInt()
            self.size = br.readUInt()

    def read_chunks_info(self, br, base_offset):
        
        br.seek(base_offset, 0)
        chunks_count = br.readUInt()

        for i in range(chunks_count):

            off = base_offset + 4 + i * 8
            br.seek(off, 0)
            nested = br.readUInt() == 1
            offset = br.readUInt()

            if nested:
                self.read_chunks_info(br, offset + base_offset)
                continue

            chunk_info = FHM.CHUNK_INFO()
            chunk_info.read(br, offset + base_offset)

            chunk = FHM.CHUNK()
            chunk.offset = chunk_info.offset + 48
            chunk.size = chunk_info.size
            chunk.type = 0
            if chunk.size >= 4:
                br.seek(chunk.offset)
                #chunk.type = br.bytesToString(br.readBytes(4)).replace("\0", "")
                chunk.type = br.readUInt()

            self.m_chunks.append(chunk)


            


