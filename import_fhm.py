from msilib.schema import Binary
import bpy
import bmesh

import gzip
import os
import struct

from math import *

from .fhm import *
from .Utilities import *
from .Blender import*

def main(filepath, clear_scene):
    if clear_scene:
        clearScene()

    file = open(filepath, 'rb')
    
    br = BinaryReader(file, "<")

    fhm = FHM()
    fhm.read(br)

    