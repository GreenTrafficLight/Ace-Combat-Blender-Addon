import binascii

from mathutils import *

from .Utilities import *

class NDXR:
    def __init__(self):

        self.mesh_informations = []
        self.boneFlags = []

    def read(self, br):

        NDXR_position = br.tell() - 4
        NDXR_size = br.readUInt()

        version = br.readUShort()
        
        mesh_count = br.readUShort()
        type = br.readUShort()
        boneCount = br.readUShort()
        
        poly_clump_start = br.readUInt() + 0x30
        poly_clump_size = br.readUInt()
        
        vertex_clump_start = poly_clump_start + poly_clump_size
        vertex_clump_size = br.readUInt()
        
        vertex_add_clump_start = vertex_clump_start + vertex_clump_size
        vertex_add_clump_size = br.readUInt()
        
        name_start = vertex_add_clump_start + vertex_add_clump_size

        boundingSphere = (br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat())

        objs = []
        for i in range(mesh_count):

            obj = NDXR.OBJECT_DATA()

            boundingSphere = (br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat())
            temp = br.tell() + 4
            br.seek(name_start + br.readUInt() + NDXR_position)
            obj.name = br.readString()

            br.seek(temp, 0)
            br.readUShort()
            self.boneFlags.append(br.readUShort())
            obj.singlebind = br.readShort()
            obj.polyCount = br.readUShort()
            obj.positionb = br.readInt()

            objs.append(obj)
            
        for obj in objs:

            for i in range(obj.polyCount):

                poly_data = NDXR.POLY_DATA()

                poly_data.polyStart = br.readInt() + poly_clump_start
                poly_data.vertStart = br.readInt() + vertex_clump_start
                poly_data.verAddStart = br.readInt() + vertex_add_clump_start
                poly_data.vertCount = br.readUShort()
                poly_data.vertSize = br.readByte()
                poly_data.UVSize = br.readByte()
                poly_data.texprop1 = br.readInt()
                poly_data.texprop2 = br.readInt()
                poly_data.texprop3 = br.readInt()
                poly_data.texprop4 = br.readInt()
                poly_data.polyCount = br.readUShort()
                poly_data.polySize = br.readByte()
                poly_data.polyFlag = br.readByte()
                br.seek(0xC, 1)

                temp = br.tell()

                br.seek(temp)


    class OBJECT_DATA :

        def __init__(self) -> None:
            
            self.singlebind = 0
            self.polyCount = 0
            self.positionb = 0
            self.name = ""

    class POLY_DATA:

        def __init__(self) -> None:
            
            self.polyStart = 0
            self.vertStart = 0
            self.verAddStart = 0
            self.vertCount = 0
            self.vertSize = 0
            self.UVSize = 0
            self.texprop1 = 0
            self.texprop2 = 0
            self.texprop3 = 0
            self.texprop4 = 0
            self.polyCount = 0
            self.polySize = 0
            self.polyFlag = 0