from distutils.command.build import build
from msilib.schema import Binary
from operator import add
import bpy
import bmesh

import gzip
import os
import struct

from math import *

from .fhm import *
from .Utilities import *
from .Blender import*

def build_mnt(data):

    index = 0

    for mnt in data.mnt_list:

        if mnt != None:

            ndxr = data.ndxr_list[index]
            mop2 = data.mop2_list[index]

            bone_mapping = []

            name_index = 0

            bpy.ops.object.add(type="ARMATURE")
            ob = bpy.context.object
            ob.rotation_euler = ( radians(90), 0, 0 )
            ob.name = mnt.names[name_index]

            amt = ob.data
            amt.name = mnt.names[name_index]

            for node in mnt.nodes:

                bone_mapping.append(mnt.names[name_index])

                bpy.ops.object.mode_set(mode='EDIT', toggle=False)
                bone = amt.edit_bones.new(mnt.names[name_index])

                bone.tail = (0, 0, 1)

                if node.parent_index != -1:

                    bone.parent = amt.edit_bones[mnt.names[node.parent_index]]

                name_index += 1

            bpy.ops.object.mode_set(mode='OBJECT')

            empty_list = []

            name_index = 0

            for node in mnt.nodes:

                translation = (0, 0, 0)
                quaternion = Quaternion((1, 0, 0, 0))

                if mop2 != None:

                    if "basepose" in mop2.kfm1_dict:
                        translation = mop2.kfm1_dict["basepose"].translations[name_index]
                        quaternion = mop2.kfm1_dict["basepose"].quaternions[name_index]

                if node.index == 0:
                    empty = add_empty(mnt.names[name_index], ob, translation, quaternion.to_euler())
                else:
                    empty = add_empty(mnt.names[name_index], empty_location=translation, empty_rotation=quaternion.to_euler())

                if node.parent_index != -1:

                    empty.parent = empty_list[node.parent_index]

                empty_list.append(empty)

                name_index += 1
            
            if index < len(data.ndxr_list) and data.ndxr_list[index] != None:

                build_ndxr(data.ndxr_list[index], empty_list, ob)

        index += 1

def build_ndxr(data, empty_list, ob):

    for ndxr_mesh in data.meshes :

        mesh = bpy.data.meshes.new(ndxr_mesh.text)
        obj = bpy.data.objects.new(ndxr_mesh.text, mesh)

        if ndxr_mesh.singlebind != -1:

            empty = empty_list[ndxr_mesh.singlebind]

            empty.users_collection[0].objects.link(obj)

        else:

            empty = add_empty(ndxr_mesh.text, ob)

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
                mesh.normals_split_custom_set_from_vertices(normals)

            last_vertex_count += len(submesh.vertices["positions"])

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
    
    br = BinaryReader(file, "<")

    fhm = FHM()
    fhm.read(br)

    build_fhm(fhm, os.path.splitext(filename)[0])

    