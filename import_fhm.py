import bpy
import bmesh

import os

from math import *
from mathutils import *

from .Resources import *
from .memory_dump import *

from .Utilities import *
from .Blender import*

def build_mnt(data):

    nd_index = 0
    mop2_index = 0

    for mnt in data.mnts:

        if mnt != None:

            try:
                mop2 = data.mop2s[mop2_index]
            except:
                mop2 = None

            bone_mapping = []

            name_index = 0

            bpy.ops.object.add(type="ARMATURE")
            ob = bpy.context.object
            ob.rotation_euler = ( radians(90), 0, 0 )
            ob.name = mnt.names[name_index]

            amt = ob.data
            amt.name = mnt.names[name_index]

            # Add bones

            """
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

                bone.head = (0.1 , 0.1, 0.1)

                mat = quaternion.to_matrix().to_4x4()
                mat = Matrix.Translation(translation) @ mat
                bone.matrix = mat

                if node.parent_index != -1:

                    parent = mnt[0].names[node.parent_index]

                    bone.parent = amt.edit_bones[parent]
                    bone.matrix = amt.edit_bones[parent].matrix @ bone.matrix

                    bone.tail = bone.matrix.translation

                name_index += 1

            name_index = 0

            bones = amt.edit_bones
            for node in mnt[0].nodes:

                bone = bones[mnt[0].names[name_index]]

                if node.parent_index != -1:

                    parent = mnt[0].names[node.parent_index]
                    
                    bone.head = bones[parent].tail
            
                name_index += 1
            """

            bpy.ops.object.mode_set(mode='OBJECT')

            # Add empty

            empty_list = []

            name_index = 0

            for node in mnt.nodes:

                translation = (0, 0, 0)
                quaternion = Quaternion((1, 0, 0, 0))

                if mop2 != None:

                    print("test")
                    """
                    if "basepose" in mop2.kfm1_dict and name_index < len(mop2.kfm1_dict["basepose"].translations) and name_index < len(mop2.kfm1_dict["basepose"].quaternions):
                        translation = mop2.kfm1_dict["basepose"].translations[name_index]
                        quaternion = mop2.kfm1_dict["basepose"].quaternions[name_index]

                    else:
                        print("Error")
                    """

                if node.index == 0:
                    empty = add_empty(mnt.names[name_index], ob, translation, quaternion.to_euler())
                else:
                    empty = add_empty(mnt.names[name_index], empty_location=translation, empty_rotation=quaternion.to_euler())

                if node.parent_index != -1:

                    empty.parent = empty_list[node.parent_index]

                empty_list.append(empty)

                name_index += 1

            # Build ND
            
            if nd_index < len(data.nds):

                nd = data.nds[nd_index]

                if nd != None:

                    build_nd(nd, empty_list, ob, bone_mapping)

                nd_index += 1
                mop2_index += 1

        else:
            nd_index += 1
            mop2_index += 1

    return nd_index

def build_nd(data, empty_list = [], ob = None, bone_mapping = None, mnt_list_is_empty = False, empty = None):

    for nd_mesh in data.groups :

        mesh = bpy.data.meshes.new(nd_mesh.name)
        obj = bpy.data.objects.new(nd_mesh.name, mesh)

        """
        if ob != None:

            modifier = obj.modifiers.new(ob.name, type="ARMATURE")
            modifier.object = bpy.data.objects[ob.name]
        """

        if not mnt_list_is_empty:

            if nd_mesh.header.bone_idx != -1:

                try:
                    empty = empty_list[nd_mesh.header.bone_idx]
                except:
                    empty = add_empty(nd_mesh.name, ob)

                empty.users_collection[0].objects.link(obj)

            else:

                empty = add_empty(nd_mesh.name, ob)

                empty.users_collection[0].objects.link(obj)

        else:

            empty.users_collection[0].objects.link(obj)

        obj.parent = empty

        vertexList = {}
        facesList = []
        normals = []

        last_vertex_count = 0

        for render_group in nd_mesh.render_groups :

            bm = bmesh.new()
            bm.from_mesh(mesh)

            # Set vertices
            for j in range(len(render_group.vertices["positions"])):
                vertex = bm.verts.new(render_group.vertices["positions"][j])

                if render_group.vertices["normals"] != []:
                    vertex.normal = render_group.vertices["normals"][j]
                    normals.append(render_group.vertices["normals"][j])
                            
                vertex.index = last_vertex_count + j

                vertexList[last_vertex_count + j] = vertex

            faces = StripToTriangle(render_group.indices)

            # Set faces
            for j in range(0, len(faces)):
                try:
                    face = bm.faces.new([vertexList[faces[j][0] + last_vertex_count], vertexList[faces[j][1] + last_vertex_count], vertexList[faces[j][2] + last_vertex_count]])
                    face.smooth = True
                    facesList.append([face, [vertexList[faces[j][0] + last_vertex_count], vertexList[faces[j][1] + last_vertex_count], vertexList[faces[j][2]] + last_vertex_count]])
                except:
                    pass

            if render_group.vertices["uvs"] != []:

                uv_name = "UV1Map"
                uv_layer1 = bm.loops.layers.uv.get(uv_name) or bm.loops.layers.uv.new(uv_name)

                for f in bm.faces:
                    for l in f.loops:
                        if l.vert.index >= last_vertex_count:
                            l[uv_layer1].uv = [render_group.vertices["uvs"][l.vert.index - last_vertex_count][0], 1 - render_group.vertices["uvs"][l.vert.index - last_vertex_count][1]]
                   
            if render_group.vertices["uvs2"] != []:

                uv_name = "UV2Map"
                uv_layer2 = bm.loops.layers.uv.get(uv_name) or bm.loops.layers.uv.new(uv_name)

                for f in bm.faces:
                    for l in f.loops:
                        if l.vert.index >= last_vertex_count:
                            l[uv_layer2].uv = [render_group.vertices["uvs2"][l.vert.index - last_vertex_count][0], 1 - render_group.vertices["uvs2"][l.vert.index - last_vertex_count][1]]

            """
            if submesh.vertices["colors"] != []:

                color_name = "Color"
                color_layer = bm.loops.layers.color.get(color_name) or bm.loops.layers.color.new(color_name)

                for f in bm.faces:
                    for l in f.loops:
                        if l.vert.index >= last_vertex_count:
                            l[color_layer].uv = [submesh.vertices["colors"][l.vert.index - last_vertex_count][0], 1 - submesh.vertices["colors"][l.vert.index - last_vertex_count][1]]
            """

            bm.to_mesh(mesh)
            bm.free()

            """
            if bone_mapping != []:
                for i in range(len(submesh.vertices["boneIds"])):
                    if submesh.vertices["boneIds"] != []:
                        vg = submesh.vertices["boneIds"][i]
                        vg_name = bone_mapping[vg + 1]
                        if not vg_name in obj.vertex_groups:
                            group = obj.vertex_groups.new(name=vg_name)
                        else:
                            group = obj.vertex_groups[vg_name]
                        weight = submesh.vertices["boneWeights"][i]
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

            last_vertex_count += len(render_group.vertices["positions"])

def build_memory_dump(memory_dump, filename):

        if memory_dump.mnt_list != []:
            
            nd_index = build_mnt(memory_dump)

            if nd_index < len(memory_dump.nd_list):

                bpy.ops.object.add(type="ARMATURE")
                ob = bpy.context.object
                ob.rotation_euler = ( radians(90), 0, 0 )
                ob.name = filename + "_remaining_nd"

                # Build ND that doesn't have MNT

                for i in range(nd_index, len(memory_dump.nd_list)):

                    empty = add_empty(str(i), ob)

                    build_nd(memory_dump.nd_list[i][0], mnt_list_is_empty=True, empty = empty)

        elif memory_dump.nd_list != [] and memory_dump.mnt_list == []:

            bpy.ops.object.add(type="ARMATURE")
            ob = bpy.context.object
            ob.rotation_euler = ( radians(90), 0, 0 )
            ob.name = filename

            for i in range (len(memory_dump.nd_list)):
                
                empty = add_empty(str(i), ob)

                build_nd(memory_dump.nd_list[i][0], mnt_list_is_empty=True, empty = empty)

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

    br = BinaryReader(file, ">")

    if file_extension == ".fhm":
        
        fhm = FHM_MESH()
        fhm.load(br)
        build_fhm(fhm, filename)



   

    