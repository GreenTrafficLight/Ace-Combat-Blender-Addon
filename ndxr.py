import binascii

from mathutils import *

from .Utilities import *

class NDXR:
    def __init__(self, br):
        self.br = br

        self.mesh_informations = []

        self.NDWD_position = 0

    def read(self, br):

        self.NDWD_position = br.tell()
        header = br.bytesToString(br.readBytes(4)).replace("\0", "")
        fileSize = br.readUInt()

        version = br.readUShort()
        
        mesh_count = br.readUShort()
        type = br.readUShort()
        boneCount = br.readUShort()
        
        self.face_buffer_start = br.readUInt() + 0x30
        self.face_buffer_size = br.readUInt()
        
        self.vertex_buffer_start = self.face_buffer_start + self.face_buffer_size
        self.vertex_buffer_size = br.readUInt()
        
        self.vertexAddBufferStart = self.vertex_buffer_start + self.vertex_buffer_size
        self.vertexAddBufferSize = br.readUInt()
        
        self.meshNameOffset = self.vertexAddBufferStart + self.vertexAddBufferSize

        boundingSphere = (br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat())

        self.read_mesh_informations(br, mesh_count)
        self.read_submesh_informations()
        
        self.get_materials()
        self.get_buffers()
        self.get_names()

    def read_mesh_informations(self, br, mesh_count):

        for i in range(mesh_count):

            mesh_information = {
                "mesh_name_offset" : 0,
                "submesh_count" : 0,
                "submesh_informations" : [],

                "mesh_name": None
            }

            boundingSphere = (br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat(), br.readFloat())
            #temp = br.tell() + 4
            #br.seek(self.meshNameOffset + br.readUInt())
            
            mesh_information["mesh_name_offset"] = br.readUInt() + self.meshNameOffset
            br.readUInt()
            br.readUShort()
            mesh_information["submesh_count"] = br.readUShort()
            br.readUInt()

            self.mesh_informations.append(mesh_information)

    def read_submesh_informations(self, br):

        for mesh_informations in self.mesh_informations:

            for i in range(mesh_informations["submesh_count"]):

                submesh_information = {
                    "face_buffer_offset" : 0,
                    "vertex_buffer_offset" : 0,
                    "vertex_add_buffer_offset" : 0,
                    "vertex_count" : 0,
                    "vertex_flag" : 0,
                    "uv_flag" : 0,
                    "material_properties_offset" : 0,
                    "face_count" : 0,

                    "material_properties" :
                        {
                            "textures_properties" : [],
                        },
                    "face_buffer" : [],
                    "vertex_buffer" : 
                        {
                        "positions" : [],
                        "colors" : [],
                        "normals" : [],
                        "texCoords1" : [],
                        "texCoords2" : []
                        }
                }

                submesh_information["face_buffer_offset"] = br.readUInt() + self.face_buffer_start
                submesh_information["vertex_buffer_offset"] = br.readUInt() + self.vertex_buffer_start
                submesh_information["vertex_add_buffer_offset"] = br.readUInt() + self.vertexAddBufferStart
                submesh_information["vertex_count"] = br.readUShort()
                submesh_information["vertex_flag"] = br.readByte()
                submesh_information["uv_flag"] = br.readByte()
                submesh_information["material_properties_offset"] = br.readUInt()
                br.readUInt()
                br.readUInt()
                br.readUInt()
                submesh_information["face_count"] = br.readUShort()
                br.readByte()
                br.readByte()
                br.seek(12, 1)

                mesh_informations["submesh_informations"].append(submesh_information)

    def get_materials(self, br):

        for mesh_informations in self.mesh_informations:

            for submesh_information in mesh_informations["submesh_informations"]:

                br.seek(submesh_information["material_properties_offset"] + self.NDWD_position, 0)
                
                br.readUShort()
                br.readUShort()
                br.readBytes(4) # zeros
                br.readUShort()
                texture_count = br.readUShort() # count ?
                br.readUInt()
                br.readUShort()
                br.readUShort()
                br.readBytes(12) # zeros
                
                for i in range(texture_count):
                    texture_properties = {
                        "texture_name" : ""
                    }

                    texture_properties["texture_name"] = str(binascii.hexlify(br.readBytes(4)), "ascii") # texture name
                    br.readBytes(8) # zeros
                    br.readByte() # ?
                    br.readByte() # ? 
                    br.readByte() # ? 
                    br.readByte() # ?
                    br.readByte() # ?
                    br.readByte() # ?
                    br.readByte() # ?
                    br.readByte() # ?
                    br.readBytes(4) # ?

                    submesh_information["material_properties"]["textures_properties"].append(texture_properties)

                br.readBytes(16) # zeros ?

    def get_buffers(self):

        for mesh_informations in self.mesh_informations:

            for submesh_information in mesh_informations["submesh_informations"]:
                
                self.br.seek(submesh_information["face_buffer_offset"] + self.NDWD_position, 0)
                self.read_face_buffer(submesh_information)

                self.br.seek(submesh_information["vertex_buffer_offset"] + self.NDWD_position, 0)
                self.read_vertex_buffer(submesh_information)

                #self.br.seek(submesh_information["vertex_add_buffer_offset"], 0)


    def read_face_buffer(self, submesh_information):
        for i in range(submesh_information["face_count"]):
            submesh_information["face_buffer"].append(self.br.readUShort())

    def read_vertex_buffer(self, submesh_information):
        for i in range(submesh_information["vertex_count"]):
            submesh_information["vertex_buffer"]["positions"].append([self.br.readFloat(), self.br.readFloat(),self.br.readFloat()])
            
            if submesh_information["vertex_flag"] >= 0x6:
                nx = self.br.readHalfFloat()
                ny = self.br.readHalfFloat()
                nz = self.br.readHalfFloat()
                nq = self.br.readHalfFloat()
                submesh_information["vertex_buffer"]["normals"].append(Vector((nx,ny,nz)).normalized())
                
                if submesh_information["vertex_flag"] == 0x7:
                    self.br.seek(16, 1) 
                #elif submesh_information["vertex_flag"] == 0x11: # FIX
                    #self.br.seek(4, 1)     

                if submesh_information["uv_flag"] == 0x10:
                    submesh_information["vertex_buffer"]["texCoords1"].append([self.br.readHalfFloat(), self.br.readHalfFloat()])
                
                if submesh_information["uv_flag"] >= 0x12:
                    submesh_information["vertex_buffer"]["colors"].append([self.br.readUByte() / 255, self.br.readUByte() / 255,self.br.readUByte() / 255, self.br.readUByte() / 255])
                    submesh_information["vertex_buffer"]["texCoords1"].append([self.br.readHalfFloat(), self.br.readHalfFloat()])
                
                if submesh_information["uv_flag"] >= 0x22:
                    submesh_information["vertex_buffer"]["texCoords2"].append([self.br.readHalfFloat(), self.br.readHalfFloat()])

    def read_vertex_add_buffer(self, submesh_information):
        pass

    def get_names(self):
        for mesh_information in self.mesh_informations:
            self.br.seek(mesh_information["mesh_name_offset"] + self.NDWD_position, 0)
            mesh_information["mesh_name"] = self.br.readString()