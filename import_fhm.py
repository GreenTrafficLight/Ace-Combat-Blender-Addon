import bpy
import bmesh

import gzip
import os
import struct

from math import *
from mathutils import *

from .fhm import *
from .memory_dump import *
from .Utilities import *
from .Blender import*

def build_mnt(data):

    nd_index = 0
    mop2_index = 0

    for mnt in data.mnt_list:

        if mnt != None:

            mop2 = data.mop2_list[mop2_index][0]

            bone_mapping = []

            name_index = 0

            bpy.ops.object.add(type="ARMATURE")
            ob = bpy.context.object
            ob.rotation_euler = ( radians(90), 0, 0 )
            ob.name = mnt[0].names[name_index]

            amt = ob.data
            amt.name = mnt[0].names[name_index]

            for node in mnt[0].nodes:

                translation = (0, 0, 0)
                quaternion = Quaternion((1, 0, 0, 0))

                if mop2 != None:

                    if "basepose" in mop2.kfm1_dict and name_index < len(mop2.kfm1_dict["basepose"].translations) and name_index < len(mop2.kfm1_dict["basepose"].quaternions):
                        translation = mop2.kfm1_dict["basepose"].translations[name_index]
                        quaternion = mop2.kfm1_dict["basepose"].quaternions[name_index]

                bone_mapping.append(mnt[0].names[name_index])

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bone = amt.edit_bones.new(mnt[0].names[name_index])

                bone.tail = (0, 0, 1)

                #mat = quaternion.to_matrix().to_4x4()
                #mat = Matrix.Translation(translation) @ mat
                #bone.matrix = mat

                if node.parent_index != -1:

                    parent = mnt[0].names[node.parent_index]

                    bone.parent = amt.edit_bones[parent]
                    #bone.matrix = amt.edit_bones[parent].matrix @ bone.matrix

                    #bone.head = translation

                name_index += 1

            """
            bones = amt.edit_bones
            for node in mnt.nodes:

                if node.parent_index != -1:

                    parent = mnt.names[node.parent_index]
                    
                    bone.tail = bones[parent].head
            """

            bpy.ops.object.mode_set(mode='OBJECT')

            empty_list = []

            name_index = 0

            for node in mnt[0].nodes:

                translation = (0, 0, 0)
                quaternion = Quaternion((1, 0, 0, 0))

                if mop2 != None:

                    if "basepose" in mop2.kfm1_dict and name_index < len(mop2.kfm1_dict["basepose"].translations) and name_index < len(mop2.kfm1_dict["basepose"].quaternions):
                        translation = mop2.kfm1_dict["basepose"].translations[name_index]
                        quaternion = mop2.kfm1_dict["basepose"].quaternions[name_index]

                    else:
                        print("test")

                if node.index == 0:
                    empty = add_empty(mnt[0].names[name_index], ob, translation, quaternion.to_euler())
                else:
                    empty = add_empty(mnt[0].names[name_index], empty_location=translation, empty_rotation=quaternion.to_euler())

                if node.parent_index != -1:

                    empty.parent = empty_list[node.parent_index]

                empty_list.append(empty)

                name_index += 1
            
            if nd_index < len(data.nd_list):

                if mnt[1] == 0x41 or mnt[1] == 0x46:

                    for i in range(4):

                        nd = data.nd_list[nd_index][0]

                        if nd != None:

                            build_ndxr(nd, empty_list, ob)

                        nd_index += 1

                else:

                    nd = data.nd_list[nd_index][0]

                    if nd != None:

                        build_ndxr(nd, empty_list, ob)

                    nd_index += 1
                    mop2_index += 1

        else:
            nd_index += 1
            mop2_index += 1

def build_ndxr(data, empty_list = [], ob = None, mnt_list_is_empty = False, empty = None):

    for ndxr_mesh in data.meshes :

        mesh = bpy.data.meshes.new(ndxr_mesh.text)
        obj = bpy.data.objects.new(ndxr_mesh.text, mesh)

        if not mnt_list_is_empty:

            if ndxr_mesh.singlebind != -1:

                empty = empty_list[ndxr_mesh.singlebind]

                empty.users_collection[0].objects.link(obj)

            else:

                empty = add_empty(ndxr_mesh.text, ob)

                empty.users_collection[0].objects.link(obj)

        else:

            empty.users_collection[0].objects.link(obj)

        obj.parent = empty

        vertexList = {}
        facesList = []
        normals = []

        last_vertex_count = 0

        for submesh in ndxr_mesh.subMeshes :

            bm = bmesh.new()
            bm.from_mesh(mesh)

            # Set vertices
            for j in range(len(submesh.vertices["positions"])):
                vertex = bm.verts.new(submesh.vertices["positions"][j])

                if submesh.vertices["normals"] != []:
                    vertex.normal = submesh.vertices["normals"][j]
                    normals.append(submesh.vertices["normals"][j])
                            
                vertex.index = last_vertex_count + j

                vertexList[last_vertex_count + j] = vertex

            faces = StripToTriangle(submesh.indices)

            # Set faces
            for j in range(0, len(faces)):
                try:
                    face = bm.faces.new([vertexList[faces[j][0] + last_vertex_count], vertexList[faces[j][1] + last_vertex_count], vertexList[faces[j][2] + last_vertex_count]])
                    face.smooth = True
                    facesList.append([face, [vertexList[faces[j][0] + last_vertex_count], vertexList[faces[j][1] + last_vertex_count], vertexList[faces[j][2]] + last_vertex_count]])
                except:
                    pass

            if submesh.vertices["uvs"] != []:

                uv_name = "UV1Map"
                uv_layer1 = bm.loops.layers.uv.get(uv_name) or bm.loops.layers.uv.new(uv_name)

                for f in bm.faces:
                    for l in f.loops:
                        if l.vert.index >= last_vertex_count:
                            l[uv_layer1].uv = [submesh.vertices["uvs"][l.vert.index - last_vertex_count][0], 1 - submesh.vertices["uvs"][l.vert.index - last_vertex_count][1]]
                   
            if submesh.vertices["uvs2"] != []:

                uv_name = "UV2Map"
                uv_layer2 = bm.loops.layers.uv.get(uv_name) or bm.loops.layers.uv.new(uv_name)

                for f in bm.faces:
                    for l in f.loops:
                        if l.vert.index >= last_vertex_count:
                            l[uv_layer2].uv = [submesh.vertices["uvs2"][l.vert.index - last_vertex_count][0], 1 - submesh.vertices["uvs2"][l.vert.index - last_vertex_count][1]]

            bm.to_mesh(mesh)
            bm.free()

            """
            for i in range(len(submesh.vertices["boneIndices"])):
                if submesh.vertices["boneIndices"] != []:
                    for k, vg in enumerate(submesh.vertices["boneIndices"][i]):
                        vg_name = bone_mapping[vg + 1]
                        if not vg_name in obj.vertex_groups:
                            group = obj.vertex_groups.new(name=vg_name)
                        else:
                            group = obj.vertex_groups[vg_name]
                        weight = submesh.vertices["boneWeights"][i][k]
                        if weight > 0.0:
                            group.add([i], weight, 'REPLACE')
            """
            
            # Set normals
            mesh.use_auto_smooth = True

            if normals != []:
                try:
                    mesh.normals_split_custom_set_from_vertices(normals)
                except:
                    pass

            last_vertex_count += len(submesh.vertices["positions"])

def build_memory_dump(memory_dump, filename):

        if memory_dump.mnt_list != []:
            
            build_mnt(memory_dump)

        elif memory_dump.nd_list != [] and memory_dump.mnt_list == []:

            bpy.ops.object.add(type="ARMATURE")
            ob = bpy.context.object
            ob.rotation_euler = ( radians(90), 0, 0 )
            ob.name = filename

            for i in range (len(memory_dump.nd_list)):
                
                empty = add_empty(str(i), ob)

                build_ndxr(memory_dump.nd_list[i][0], mnt_list_is_empty=True, empty = empty)

def build_fhm(data, filename):

    #currentCollection = bpy.context.view_layer.active_layer_collection.collection
    #fhmCollection = bpy.data.collections.new(filename)
    #currentCollection.children.link(fhmCollection)

    build_mnt(data)

def main(filepath, clear_scene):
    if clear_scene:
        clearScene()

    file = open(filepath, 'rb')
    filename =  filepath.split("\\")[-1]
    file_extension =  os.path.splitext(filepath)[1]
    file_size = os.path.getsize(filepath)

    br = BinaryReader(file, "<")

    data = br.readBytes(file_size)
    br.seek(0, 0)

    if file_extension == ".fhm":
        
        fhm = FHM()
        fhm.read(br)

        build_fhm(fhm, os.path.splitext(filename)[0])
    
    elif file_extension == ".ndp3":

        memory_dump = MEMORY_DUMP()
        memory_dump.read(br, file_size)

        build_memory_dump(memory_dump, os.path.splitext(filename)[0])
        
    elif file_extension == ".ndxr":

        memory_dump = MEMORY_DUMP()
        memory_dump.read(br, file_size)

        build_memory_dump(memory_dump, os.path.splitext(filename)[0])



   

    