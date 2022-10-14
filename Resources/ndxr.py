import binascii

from mathutils import *

from ..Utilities import *

class ND:
    
    def __init__(self):

        self.size = 0

        self.groups = []

        self.submeshes_count = 0

    class HEADER:

        def __init__(self) -> None:
            self.sign = ""
            self.size = 0
            self.version = 0
            self.groups_count = 0
            self.bone_min_idx = 0
            self.bone_max_idx = 0

            self.offset_to_indices = 0
            self.indices_buffer_size = 0
            self.vertices_buffer_size = 0

            self.unknown_often_zero = 0
            self.bbox_origin = []
            self.bbox_size = 0

        def read(self, br):
            self.sign = br.bytesToString(br.readBytes(4)).replace("\0", "")
            self.size = br.readUInt()
            self.version = br.readUShort()
            self.groups_count = br.readUShort()
            self.bone_min_idx = br.readUShort()
            self.bone_max_idx = br.readUShort()

            self.offset_to_indices = br.readUInt()
            self.indices_buffer_size = br.readUInt()
            self.vertices_buffer_size = br.readUInt()
            self.vertices_clump_buffer_size = br.readUInt()
            
            self.bbox_origin = [br.readFloat(), br.readFloat(), br.readFloat()]
            self.bbox_size = br.readFloat()

    class GROUP_HEADER:

        def __init__(self) -> None:
            self.bbox_origin = []
            self.bbox_size = 0
            self.origin = []
            self.unk_zero = 0
            self.offset_to_name = 0
            self.unk = 0
            self.bone_idx = 0
            self.render_groups_count = 0
            self.offset_to_render_groups = 0

        def read(self, br):

            self.bbox_origin = [br.readFloat(), br.readFloat(), br.readFloat()]
            self.bbox_size = br.readFloat()
            self.origin = [br.readFloat(), br.readFloat(), br.readFloat()]
            self.unk_zero = br.readUInt()
            self.offset_to_name = br.readUInt()
            self.unk = br.readUInt()
            self.bone_idx = br.readShort()
            self.render_groups_count = br.readShort()
            self.offset_to_render_groups = br.readUInt()

    class RENDER_GROUP_HEADER:

        def __init__(self) -> None:
            self.ibuf_offset = 0
            self.vbuf_offset = 0
            self.vbuf_add_offset = 0
            self.vertex_count = 0
            self.vertex_format = 0
            self.offset_to_tex_info = 0
            self.unknown_zero3 = []
            self.indice_count = 0
            self.indice_format = 0
            self.unknown_zero5 = []

        def read(self, br):

            self.ibuf_offset = br.readUInt()
            self.vbuf_offset = br.readUInt()
            self.vbuf_add_offset = br.readUInt()
            self.vertex_count = br.readUShort()
            self.vertex_format = br.readUShort()
            self.offset_to_tex_info = br.readUInt()
            self.unknown_zero3 = [br.readUInt(), br.readUInt(), br.readUInt()]
            self.indice_count = br.readUShort()
            self.indice_format = br.readUShort()
            self.unknown_zero5 = [br.readUInt(), br.readUInt(), br.readUInt()]

    class TEX_INFO_HEADER:

        def __init__(self) -> None:
            self.unknown = 0
            self.unknown2 = 0
            self.unknown_zero = 0

            self.unknown3 = 0
            self.tex_info_count = 0
            self.unknown4 = 0
            self.unknown5 = 0
            self.unknown6 = 0
            self.unknown_2 = 0
            self.unknown_zero2 = []

        def read(self, br):
            self.unknown = br.readUShort()
            self.unknown2 = br.readUShort()
            self.unknown_zero = br.readUInt()

            self.unknown3 = br.readUShort()
            self.tex_info_count = br.readUShort()
            self.unknown4 = br.readUShort()
            self.unknown5 = br.readUShort()
            self.unknown6 = br.readUShort()
            self.unknown_2 = br.readUShort()
            self.unknown_zero2 = [br.readUInt() for _ in range(3)]

    class TEX_INFO:

        def __init__(self) -> None:
            self.texture_hash_id = 0
            self.unknown_zero = 0
            self.unknown_zero2 = 0

            self.unknown3 = 0
            self.unknown4 = 0
            self.unknown5 = 0
            self.unknown6 = 0

        def read(self, br):
            self.texture_hash_id = str(binascii.hexlify(br.readBytes(4)), "ascii")
            self.unknown_zero = br.readUInt()
            self.unknown_zero2 = br.readUInt()

            self.unknown3 = br.readUInt()
            self.unknown4 = br.readUShort()
            self.unknown5 = br.readUShort()
            self.unknown6 = br.readUInt()     

    class NDXR_MATERIAL_PARAM:

        def __init__(self) -> None:
            self.name = ""
            self.unknown_32_or_zero = 0
            self.offset_to_name = 0
            self.unknown = 0
            self.unknown_zero2 = 0

        def read(self, br):
            self.unknown_32_or_zero = br.readUInt()
            self.offset_to_name = br.readUInt()
            self.unknown = br.readUInt()
            self.unknown_zero2 = br.readUInt() 

    class RENDER_GROUP:
        
        def __init__(self) -> None:
            self.header = None
            self.tex_header  = None
            self.tex_infos = []
            self.material_params = []
            self.vertices = None
            self.indices = []

    class GROUP:
        
        def __init__(self) -> None:
            self.name = ""
            self.header = None
            self.render_groups = []

    def read(self, br):

        NDXR_POSITION = br.tell()
        header = ND.HEADER()
        header.read(br)

        groups = []
        for i in range(header.groups_count):
            group = ND.GROUP()
            group.header = ND.GROUP_HEADER()
            group.header.read(br)
            self.groups.append(group)

        strings_offset = header.offset_to_indices + 48 + header.indices_buffer_size + header.vertices_buffer_size + header.vertices_clump_buffer_size + NDXR_POSITION
        br.seek(strings_offset, 0)

        for group in self.groups:

            br.seek(group.header.offset_to_render_groups + NDXR_POSITION)
            for i in range(group.header.render_groups_count):
                render_group = ND.RENDER_GROUP()
                render_group.header = ND.RENDER_GROUP_HEADER()
                render_group.header.read(br)
                group.render_groups.append(render_group)

            br.seek(strings_offset + group.header.offset_to_name)
            group.name = br.readString()

        for group in self.groups:

            for render_group in group.render_groups:

                br.seek(render_group.header.offset_to_tex_info + NDXR_POSITION)
                render_group.tex_header = ND.TEX_INFO_HEADER()
                render_group.tex_header.read(br)

                for ti in range(render_group.tex_header.tex_info_count):
                    tex_info = ND.TEX_INFO()
                    tex_info.read(br)
                    render_group.tex_infos.append(tex_info)

                while True:
                    p = ND.NDXR_MATERIAL_PARAM()
                    p.read(br)

                    render_group.material_params.append(p)

                    if p.unknown_32_or_zero == 0:
                        break

                for p in render_group.material_params:

                    br.seek(strings_offset + p.offset_to_name)
                    p.name = br.readString()

        for i in range(header.groups_count):

            gf = self.groups[i]

            for j in range(len(gf.render_groups)):

                rgf = gf.render_groups[j]

                br.seek(header.offset_to_indices + 48 + header.indices_buffer_size + rgf.header.vbuf_offset + NDXR_POSITION)

                #print(br.tell())

                rgf.vertices = self.readVertex(br, header, NDXR_POSITION, gf, rgf)

                br.seek(header.offset_to_indices + 48 + rgf.header.ibuf_offset + NDXR_POSITION)

                for k in range(rgf.header.indice_count):

                    rgf.indices.append(br.readUShort())

    def readVertex(self, br, header, NDXR_POSITION, gf, rgf):

        format = rgf.header.vertex_format

        boneType = ((format >> 8) & 0xFF) & 0xF0
        vertexType = ((format >> 8) & 0xFF) & 0xF

        uv_count = format >> 12
        has_tbn = format & (1 << 0)
        has_skining = (format & (1 << 4)) > 0
        has_normal  = (format & (1 << 8)) > 0
        has_color  = (format & (1 << 9)) > 0

        vertices = {
            "positions" : [],
            "normals": [],
            "bitans" : [],
            "tans" : [],
            "colors" : [],
            "uvs" : [],
            "uvs2" : [],
            "boneIds" : [],
            "boneWeights" : []
        }

        if (boneType > 0):

            #print(br.tell())
            vertices = self.readUV(br, format, rgf, vertices)
            br.seek(header.offset_to_indices + 48 + header.indices_buffer_size + header.vertices_buffer_size + rgf.header.vbuf_add_offset + NDXR_POSITION)
            #print(br.tell())

        for i in range(rgf.header.vertex_count):

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
                
                normals = [br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()]
                scalar = br.readHalfFloat()
                vertices["normals"].append(Vector((normals[0] * scalar, normals[1] * scalar, normals[2] * scalar)).normalized())

            elif (vertexType == 0x7):

                normals = [br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()]
                scalar = br.readHalfFloat()
                vertices["normals"].append(Vector((normals[0] * scalar, normals[1] * scalar, normals[2] * scalar)).normalized())

                vertices["bitans"].append([br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()])
                vertices["tans"].append([br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat(), br.readHalfFloat()])

            if (boneType == 0x0):

                if (format & 0xFF >= 18 and (format >> 8) & 0xFF <= 32):

                    vertices["colors"].append([br.readByte(), br.readByte(), br.readByte(), br.readByte()])

                # UV Data

                if (format & 0xFF == 16):
                    vertices["uvs"].append([br.readHalfFloat(), br.readHalfFloat()])
                
                elif (format & 0xFF == 17):
                    vertices["uvs"].append([br.readFloat(), br.readFloat()])    

                elif (format & 0xFF == 19):
                    vertices["uvs"].append([br.readFloat(), br.readFloat()])   

                elif (format & 0xFF == 33):
                    vertices["uvs"].append([br.readFloat(), br.readFloat()])
                    vertices["uvs2"].append([br.readFloat(), br.readFloat()])
                    
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

                vertices["boneIds"].append(gf.header.bone_idx)
                vertices["boneWeights"].append(1)                   

        return vertices

    def readUV(self, br, format, rgf, vertices):

        uvCount = (format & 0xFF) >> 4
        uvType = (format & 0xFF) & 0xF

        for i in range(rgf.header.vertex_count):

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


