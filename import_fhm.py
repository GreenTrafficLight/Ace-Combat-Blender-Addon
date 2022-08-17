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

def build_fhm(data, filename):

    #currentCollection = bpy.context.view_layer.active_layer_collection.collection
    #fhmCollection = bpy.data.collections.new(filename)
    #currentCollection.children.link(fhmCollection)

    root = add_empty(filename)

    index = 0

    for ndxr in data.ndxr_list:

        ndxr_empty = add_empty("ndxr_" + str(index), root, empty_rotation=( radians(90), 0, 0 ))

        for ndxr_mesh in ndxr.meshes :

            mesh = bpy.data.meshes.new(ndxr_mesh.text)
            obj = bpy.data.objects.new(ndxr_mesh.text, mesh)

            ndxr_empty.users_collection[0].objects.link(obj)

            obj.parent = ndxr_empty

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

                # Set normals
                mesh.use_auto_smooth = True

                if normals != []:
                    mesh.normals_split_custom_set_from_vertices(normals)


                last_vertex_count += len(submesh.vertices["positions"])


        index += 1

def main(filepath, clear_scene):
    if clear_scene:
        clearScene()


    file = open(filepath, 'rb')
    filename =  filepath.split("\\")[-1]
    
    br = BinaryReader(file, "<")

    fhm = FHM()
    fhm.read(br)

    build_fhm(fhm, os.path.splitext(filename)[0])

    