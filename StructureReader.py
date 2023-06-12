from math import pi
from plyfile import PlyData
from PolyscopeObject import PolyscopeObject
import polyscope as ps
import numpy as np
import os
import json
import cv2


class StructureReader():
    def __init__(self, folder_path, deep = False, render = False, process = True) -> None:
        self.folder_path = folder_path
        self.number = str(folder_path).split("\\")[-1]
        self.ply_file_path = self.number + ".ply"
        self.json_file_path = self.number + ".json"
        self.deep = deep
        self.render = render
        self.process = process

        self.vertices = None
        self.faces = None
        self.color_quantity = None
        self.pattern_archetypes = None
        self.patterns = None

        self.read_ply_file()
        self.texturize()
        self.read_json_file()


    def read_ply_file(self):
        try:
            with open(os.path.join(self.folder_path, self.ply_file_path), "rb") as file:
                data = PlyData.read(file)
                for comment in data.comments:
                    if (comment.endswith(".jpg")):
                        self.texture_file_path = os.path.join(self.folder_path, comment.split(" ")[-1])
                self.vertices = np.array(list([x, y, z] for x, y, z, _, _, _ in data["vertex"].data))
                self.faces = np.array(list(indexes for indexes, _ in data["face"].data))
                face_texture_coordinates = np.array(list(coordinates for _, coordinates in data["face"].data))
                face_texture_coordinates = np.reshape(face_texture_coordinates, (len(data["face"].data)*3, 2))
                self.face_texture_coordinates = np.array(list(map(lambda x : [x[0], 1-x[1]], face_texture_coordinates)))
        except:
            print(f"No .ply file at {self.folder_path}")
            return


    def texturize(self):
        try:
            im = cv2.imread(self.texture_file_path)
        except:
            if self.texture_file_path:
                print(f"No texture file at {self.texture_file_path}")
            else:
                print(f"No texture file route specified")
            return 
        n_faces = self.faces.shape[0]
        height, width, _ = im.shape

        textured_vertices = {}
        for i in range(n_faces):
            points = self.faces[i]
            for e in range(len(points)):
                if not points[e] in textured_vertices.keys():
                    vertex_texture_coord = self.face_texture_coordinates[i*3+e]
                    vertex_color = im[int(vertex_texture_coord[1] * height)][int(vertex_texture_coord[0] * width)]
                    textured_vertices[points[e]] = vertex_color

        for i in range(self.vertices.shape[0]):
            if not i in textured_vertices.keys():
                textured_vertices[i] = (255,255,255)

        self.color_quantity = []
        for id in sorted(textured_vertices.keys()):
            point_color = textured_vertices[id]
            self.color_quantity.append([point_color[2]/255, point_color[1]/255, point_color[0]/255])
        self.color_quantity = np.array(self.color_quantity)


    def read_json_file(self):
        try:
            json_file = open(os.path.join(self.folder_path, self.json_file_path), "r")
        except:
            print(f"No tag json file at {self.folder_path}")
            return
        self.pattern_archetypes = {}
        data = json.load(json_file)
        for archetype in data["annotations"]:
            arch_id = archetype["patternId"]
            self.pattern_archetypes[arch_id] = {# "fileName": archetype["fileName"],
                                                # "foldSymmetry": archetype["foldSymmetry"],
                                                "selections": []}
            for selection in archetype["selections"]:
                instance = {# "flipped": selection["flipped"],
                            # "rotation": selection["rotation"],
                            # "scale": selection["scale"],
                            # "polygonPts": selection["polygonPts"],
                            "faceIdxs": selection["faceIdxs"]}
                self.pattern_archetypes[arch_id]["selections"].append(instance)
        json_file.close()


    def CreatePolyscopeObject(self):
        return PolyscopeObject(self.folder_path, self.number, self.vertices, self.faces, self.color_quantity, self.pattern_archetypes, self.deep, self.render, self.process)