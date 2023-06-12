import polyscope as ps
import numpy as np
from Cylinder import Cylinder
import os
from Heatmap import Heatmap
import json


class PolyscopeObject():
    def __init__(self,folder_path, name, vertices, faces, texture, tags, deep = False, render = True, process = True):
        self.folder_path = folder_path
        self.name = name
        self.vertices = vertices
        self.faces = faces
        self.texture = texture
        self.tags = tags

        self.patterns = None
        self.centroids = None
        self.projected_centroids = None
        self.projection_mesh = None
        self.centroid_projections_faces = None
        self.centroid_projections_vertices = None
        self.heatmap = None

        self.DEEP = deep
        self.RENDER = render
        self.PROCESS = process

        self.get_patterns()
        self.calculate_centroids()
        self.project_cylinder_center()
        self.generate_heatmap()
        self.generate_projection_meshes()


    def get_patterns(self):
        if (self.RENDER):
            self.patterns = []
            for archetype_key in self.tags:
                archetype = self.tags[archetype_key]
                archetype_faces = []
                for selection in archetype["selections"]:
                    archetype_faces += list(self.faces[i] for i in selection["faceIdxs"])
                self.patterns.append(archetype_faces)                


    def calculate_centroids(self):
        #self.centroids = []
        json_path = os.path.join(self.folder_path, self.name + "_centroids.json")
        if (not self.DEEP):
            try: 
                with open(json_path) as json_file:
                    self.centroids = json.load(json_file)
                return 
            except:
                pass
        if (self.PROCESS or self.RENDER):
            self.centroids = {}
            for archetype_key in self.tags:
                archetype = self.tags[archetype_key]
                archetype_centroids = []
                for selection in archetype["selections"]:
                    selection_faces = list(self.faces[i] for i in selection["faceIdxs"])
                    selection_centroid_x = 0
                    selection_centroid_y = 0
                    selection_centroid_z = 0
                    for face_ids in selection_faces:
                        vertex_id = face_ids[0]
                        control_point = self.vertices[vertex_id]
                        selection_centroid_x += control_point[0]
                        selection_centroid_y += control_point[1]
                        selection_centroid_z += control_point[2]
                    selection_centroid_x /= len(selection_faces)
                    selection_centroid_y /= len(selection_faces)
                    selection_centroid_z /= len(selection_faces)
                    archetype_centroids.append([selection_centroid_x, selection_centroid_y, selection_centroid_z])
                #self.centroids.append(archetype_centroids)
                self.centroids[archetype_key] = archetype_centroids
        
            json_object = json.dumps(self.centroids, indent=4)
            with open(json_path, "w") as json_file:
                json_file.write(json_object)   


    def project_cylinder_center(self):
        if (self.PROCESS or self.RENDER):
            self.projected_centroids = []
            #for archetype_centroids in self.centroids:
            for archetype_key in self.centroids:
                centroids = []
                #for x, y, z in archetype_centroids:
                for x, y, z in self.centroids[archetype_key]:
                    den = (x**2 + z**2) ** 0.5
                    new_x = x / den
                    new_z = z / den
                    centroids.append([new_x, y, new_z])
                self.projected_centroids.append(centroids)
        if (self.RENDER):
            self.projection_mesh = Cylinder(629, 201)


    def generate_heatmap(self):
        self.heatmap_file_path = os.path.join(self.folder_path, f"{self.name}_heatmap.png")
        self.descriptor_file_path = os.path.join(self.folder_path, f"{self.name}_descriptor.json")

        if (not self.DEEP):
            try:
                with open(self.descriptor_file_path):
                    pass
            except:
                self.heatmap = Heatmap(self.name, self.folder_path, self.projected_centroids)

            try:
                with open(self.descriptor_file_path):
                    pass
            except:
                if (self.heatmap == None):
                    self.heatmap = Heatmap(self.name, self.folder_path, self.projected_centroids)
                self.heatmap.generate_heatmap()
        
        else:
            self.heatmap = Heatmap(self.name, self.folder_path, self.projected_centroids)
            if (self.RENDER):
                self.heatmap.generate_image() 

        if (self.RENDER):
            self.projection_mesh.texturize(self.heatmap_file_path)


    def generate_projection_meshes(self):
        if (self.RENDER):
            self.centroid_projections_vertices = []
            self.centroid_projections_faces = []
            #for archetype_id in range(len(self.centroids)):
            for archetype_id in self.centroids:
                cylinder_vertices = []
                cylinder_faces = []
                for i in range(len(self.centroids[archetype_id])):
                    c_x, c_y, c_z = self.centroids[archetype_id][i]
                    p_x, p_y, p_z = self.projected_centroids[int(archetype_id)][i]
                
                    d_x = p_x - c_x
                    d_y = p_y - c_y
                    d_z = p_z - c_z

                    m_x = (p_x + c_x) / 2
                    m_y = (p_y + c_y) / 2
                    m_z = (p_z + c_z) / 2

                    d_module = (d_x ** 2 + d_y ** 2 + d_z ** 2) ** 0.5

                    cylinder = Cylinder(6, 2)
                    cylinder.set_radius(0.01)
                    cylinder.set_length(d_module)
                    cylinder.rotate(d_x, d_y, d_z)
                    cylinder.translate(m_x, m_y, m_z)

                    num_vertices = len(cylinder_vertices)
                    sum = lambda x : x + num_vertices
                    aply = lambda face_list : list(map(sum, face_list))

                    for point in cylinder.points:
                        cylinder_vertices.append(point)
            
                    for face in list(map(aply, cylinder.faces)):
                        cylinder_faces.append(face)

                self.centroid_projections_vertices.append(cylinder_vertices)
                self.centroid_projections_faces.append(cylinder_faces)

    
    def visualize(self):
        ps.init()
        mesh = ps.register_surface_mesh("object", self.vertices, self.faces)
        mesh.set_smooth_shade(True)
        try:
            mesh.add_color_quantity("color", self.texture, enabled=True)
        except:
            pass
        try:
            pattern_meshes = []
            for i in range(len(self.patterns)):
                pattern_meshes.append(ps.register_surface_mesh(f"pattern {i+1}", self.vertices * 1.001, np.array(self.patterns[i])))
                pattern_meshes[i].set_smooth_shade(True)
                pattern_meshes[i].set_transparency(0.5)
        except:
            pass
        try:
            centroids = []
            for i in range(len(self.centroids)):
                centroids.append(ps.register_point_cloud(f"pattern {i+1} centroids", np.array(self.centroids[i])))
        except:
            pass
        try:
            centroid_projections = []
            for i in range(len(self.projected_centroids)):
                centroid_projections.append(ps.register_point_cloud(f"pattern {i+1} normalized centroids", np.array(self.projected_centroids[i])))
        except:
            pass
        try:
            self.projection_mesh.visualize(ps)
        except:
            pass
        try:
            projections = []
            for i in range(len(self.centroid_projections_vertices)):
                projections.append(ps.register_surface_mesh(f"pattern {i+1} projection vectors", np.array(self.centroid_projections_vertices[i]), np.array(self.centroid_projections_faces[i])))
                projections[i].set_smooth_shade(True)
        except:
            pass
        ps.set_ground_plane_mode("none")
        ps.show()
