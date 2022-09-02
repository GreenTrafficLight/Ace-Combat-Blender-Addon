import binascii

from mathutils import *

from .Utilities import *

class NDXR:
    def __init__(self):

        self.mesh_informations = []
        self.boneFlags = []

        self.meshes = []

        self.submeshes_count = 0

    def read(self, br, endian="<"):

        br.endian = endian

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
        
        meshIndex = 0
        for obj in objs:

            mesh = NDXR.MESH()
            mesh.text = obj.name
            mesh.boneFlag = self.boneFlags[meshIndex]
            mesh.singlebind = obj.singlebind
            self.meshes.append(mesh)
            
            meshIndex += 1

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

                polygon = NDXR.POLYGON() 
                polygon.vertices = self.readVertex(br, NDXR_position, poly_data, obj)

                br.seek(poly_data.polyStart + NDXR_position, 0)

                for x in range(poly_data.polyCount):

                    polygon.indices.append(br.readUShort())

                mesh.subMeshes.append(polygon)
                self.submeshes_count += 1

                poly_data.materials = self.readMaterials(br, NDXR_position, poly_data, name_start)

                br.seek(temp)

    def readVertex(self, br, NDXR_position, poly_data, object_data):

        boneType = poly_data.vertSize & 0xF0
        vertexType = poly_data.vertSize & 0xF

        vertices = {
            "positions" : [],
            "normals": [],
            "bitans" : [],
            "tans" : [],
            "colors" : [],
            "uvs" : [],
            "boneIds" : [],
            "boneWeights" : []
        }

        br.seek(poly_data.vertStart + NDXR_position)

        #print(br.tell())

        if (boneType > 0):

            #print(br.tell())
            vertices = self.readUV(br, poly_data, object_data, vertices)
            br.seek(poly_data.verAddStart + NDXR_position, 0)
            #print(br.tell())

        for i in range(poly_data.vertCount):

            vertices["positions"].append([br.readFloat(), br.readFloat(), br.readFloat()])

            if (vertexType == 0x0):

                br.readFloat()
            
            elif (vertexType == 0x1):

                vertices["normals"].append([br.readFloat(), br.readFloat(), br.readFloat()])
                br.readBytes(4)
                br.readBytes(4)

            elif (vertexType == 0x2):

                vertices["normals"].append([br.readFloat(), br.readFloat(), br.readFloat()])
                br.readBytes(4)
                br.readBytes(12)
                br.readBytes(12)
                br.readBytes(12)          

            elif (vertexType == 0x3):
                
                br.readBytes(4)
                vertices["normals"].append([br.readFloat(), br.readFloat(), br.readFloat()])
                br.readBytes(4)
                vertices["bitans"].append([br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat()])
                vertices["tans"].append([br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat()])
                
            elif (vertexType == 0x6):

                vertices["normals"].append([br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()])
                br.readBytes(2)

            elif (vertexType == 0x7):

                vertices["normals"].append([br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()])
                br.readBytes(2)
                vertices["bitans"].append([br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()])
                vertices["tans"].append([br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()])

            #print(br.tell())

            if (boneType == 0x0):

                if (poly_data.UVSize >= 18):

                    vertices["colors"].append([br.readByte(), br.readByte(), br.readByte(), br.readByte()])


                if (poly_data.UVSize == 16):
                    vertices["uvs"].append([br.readHalfFloat(), br.readHalfFloat()])
                
                elif (poly_data.UVSize == 17):
                    vertices["uvs"].append([br.readFloat(), br.readFloat()])                  

            if (boneType == 0x10):

                vertices["boneIds"].append([br.readInt(), br.readInt(), br.readInt(), br.readInt()])
                vertices["boneWeights"].append([br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat()])

            elif (boneType == 0x20):

                vertices["boneIds"].append([br.readUShort(), br.readUShort(), br.readUShort(), br.readUShort()])
                vertices["boneWeights"].append([br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()])                    

            elif (boneType == 0x40):

                vertices["boneIds"].append([br.readByte(), br.readByte(), br.readByte(), br.readByte()])
                vertices["boneWeights"].append([br.readByte() / 255, br.readByte() / 255, br.readByte() / 255, br.readByte() / 255])                   

            elif (boneType == 0x0):

                vertices["boneIds"].append(object_data.singlebind)
                vertices["boneWeights"].append(1)                   

        return vertices

    def readUV(self, br, poly_data, object_data, vertices):

        uvCount = poly_data.UVSize >> 4
        uvType = poly_data.UVSize & 0xF

        for i in range(poly_data.vertCount):

            if (uvType == 0x0):

                for j in range(uvCount):
                    vertices["uvs"].append([br.readHalfFloat(), br.readHalfFloat()])

            elif (uvType == 0x1):

                for j in range(uvCount):
                    vertices["uvs"].append([br.readFloat(), br.readFloat()])                

            elif (uvType == 0x2):

                vertices["colors"].append([br.readByte(), br.readByte(), br.readByte(), br.readByte()])
                for j in range(uvCount):
                    vertices["uvs"].append([br.readHalfFloat(), br.readHalfFloat()])

            elif (uvType == 0x4):

                vertices["colors"].append([br.readHalfFloat() * 0xFF, br.readHalfFloat() * 0xFF, br.readHalfFloat() * 0xFF, br.readHalfFloat() * 0xFF])
                for j in range(uvCount):
                    vertices["uvs"].append([br.readHalfFloat(), br.readHalfFloat()])

        return vertices

    def readMaterials(self, br, NDXR_position, poly_data, nameOffset):

        propoff = poly_data.texprop1
        materials = []

        while propoff != 0:

            br.seek(propoff + NDXR_position, 0)

            material = NDXR.MATERIAL()
            materials.append(material)

            material.flags = br.readUInt()
            br.seek(4, 1)
            material.srcFactor = br.readUShort()
            texCount = br.readUShort()
            material.dstFactor = br.readUShort()
            material.alphaTest = br.readByte()
            material.alphaFunction = br.readByte()

            material.refAlpha = br.readUShort()
            material.cullMode = br.readUShort()
            br.seek(4, 1)
            material.unk2 = br.readInt()
            material.zBufferOffset = br.readInt()

            for i in range(texCount):

                texture = NDXR.MATERIAL.TEXTURE()
                texture.hash = str(binascii.hexlify(br.readBytes(4)), "ascii")
                br.seek(6, 1)
                texture.mapMode = br.readUShort()
                texture.wrapModeS = br.readByte()
                texture.wrapModeT = br.readByte()
                texture.minFilter = br.readByte()
                texture.magFilter = br.readByte()
                texture.mipDetail = br.readByte()
                texture.unknown = br.readByte()
                br.seek(4, 1)
                texture.unknown2 = br.readShort()
                material.textures.append(texture)

            matAttSize = -1

            while True:

                pos = br.tell()
                matAttSize = br.readInt()
                if matAttSize == 0:
                    break
                nameStart = br.readInt()
                br.seek(3, 1)
                valueCount = br.readByte()
                br.seek(4, 1)

                br.seek(nameOffset + nameStart + NDXR_position, 0)
                name = br.readString()


            if (propoff == poly_data.texprop1):
                propoff = poly_data.texprop2
            elif (propoff == poly_data.texprop2):
                    propoff = poly_data.texprop3
            elif (propoff == poly_data.texprop3):
                propoff = poly_data.texprop4

        return materials

    class OBJECT_DATA :

        def __init__(self) -> None:
            
            self.singlebind = -1
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

    class MESH:

        def __init__(self) -> None:
            
            self.text = ""
            self.boneFlag = 0
            self.singlebind = -1
            self.boundingSphere = []

            self.subMeshes = []

    class POLYGON:

        def __init__(self) -> None:
            
            self.vertices = []
            self.indices = []

            self.materials = []

    class MATERIAL:

        def __init__(self) -> None:
            
            self.flags = 0
            
            self.blendMode = 0
            self.dstFactor = 0
            self.srcFactor = 0
            
            self.alphaTest = 0
            self.alphaFunction = 0
            self.refAlpha = 0

            self.cullMode = 0

            self.unk1 = 0
            self.unk2 = 0

            self.zBufferOffset = 0

            self.displayTexId = -1

            self.glow = False

            self.hasShadow = False

            self.useVertexColor = False

            self.useReflectionColor = False

            self.textures = []

        class TEXTURE :

            def __init__(self) -> None:
                
                self.hash = None
                self.mapMode = 0
                self.wrapModeS = 1
                self.wrapModeT = 1
                self.minFilter = 3
                self.magFilter = 2
                self.mipDetail = 6
                self.unknown = 0
                self.unknown2 = 0

