from math import acos, cos, pi, sin
import numpy as np
import polyscope as ps
import cv2


class Cylinder:
    def __init__(self, dim = 8, steps = 2):
        # colection of points
        self.points = []
        # number of points on the circular cut
        self.dim = dim
        # number of points on the vertical axis
        self.steps = steps
        for e in range(steps):
            for i in range(dim):
                x = cos(i * 2 * pi / dim)
                z = sin(i * 2 * pi / dim)
                y = -1 + e * 2 / (steps - 1)
                self.points.append([x, y, z])
        # collection of faces (relation between points)
        self.faces = []
        for e in range(steps - 1):
            for i in range(dim):
                if (i != dim - 1):
                    self.faces.append([(dim*e)+i, (dim*e)+i+1, (dim*e)+dim+i])
                    self.faces.append([(dim*e)+i+1,(dim*e)+dim+i+1, (dim*e)+dim+i])
                else:
                    self.faces.append([dim*e,dim*(e+1)+i,dim*e+i])
                    self.faces.append([dim*e,dim*(e+1),dim*(e+1)+i])


    # Method to change radius of a Cylinder
    def set_radius(self, radius):
        x_sample, _, z_sample = self.points[0]
        old_radius = (x_sample**2 + z_sample**2) ** 0.5
        factor = radius / old_radius
        for i in range(len(self.points)):
            x, y, z = self.points[i]
            x *= factor
            z *= factor
            self.points[i] = [x, y, z]


    # Method to change the height of a cylinder
    def set_length(self, length):
        _, y_first_sample, _ = self.points[0]
        _, y_last_sample, _ = self.points[-1]
        old_length = y_last_sample - y_first_sample
        factor = length / old_length
        for i in range(len(self.points)):
            x, y, z = self.points[i]
            y *= factor
            self.points[i] = [x, y, z]


    # Set angle to align with the argument point
    def rotate(self, x, y, z):
        # Dip Angle
        # dot with y axis
        dip_dot = y
        # 2 dimension module
        dip_module = (x ** 2 + y ** 2) ** 0.5
        if dip_module == 0:
            dip_angle = 0
        else:
            dip_angle = acos(dip_dot / dip_module)

        # Swipe Angle
        # dot with x axis
        swipe_dot = x
        # 2 dimension module
        swipe_module = (x ** 2 + z ** 2) ** 0.5
        if swipe_module == 0:
            swipe_angle = 0
        else:
            swipe_angle = acos(swipe_dot / swipe_module)
        
        if z < 0:
            swipe_angle = 2 * pi - swipe_angle

        # Aply rotation on z axis and y axis to every point
        for i in range(len(self.points)):
            p_x, p_y, p_z =self.points[i]

            # z axis rotation
            # angle made between point on cylinder and y axis
            p_dip_dot = p_y
            p_dip_module = (p_x ** 2 + p_y ** 2) ** 0.5
            if p_dip_module == 0:
                p_dip_angle = 0
            else:
                p_dip_angle = acos(p_dip_dot / p_dip_module)

            if p_x < 0:
                p_dip_angle = - p_dip_angle

            p_x = p_dip_module * sin(dip_angle + p_dip_angle)
            p_y = p_dip_module * cos(dip_angle + p_dip_angle)


            # y axis rotation
            # angle made between point on cylinder and x axis
            p_swipe_dot = p_x
            p_swipe_module = (p_x ** 2 + p_z ** 2) ** 0.5
            if p_swipe_module == 0:
                p_swipe_angle = 0
            else:
                p_swipe_angle = acos(p_swipe_dot / p_swipe_module)

            if p_z < 0:
                p_swipe_angle = - p_swipe_angle
            

            p_x = p_swipe_module * cos(swipe_angle + p_swipe_angle)
            p_z = p_swipe_module * sin(swipe_angle + p_swipe_angle)
            
            self.points[i] = [p_x, p_y, p_z]


    # Translate a cylinder by the argument vector
    def translate(self, x, y, z):
        for i in range(len(self.points)):
            p_x, p_y, p_z = self.points[i]
            p_x += x
            p_y += y
            p_z += z
            self.points[i] = [p_x, p_y, p_z]


    # Generate a list of points on the 2D space
    def plane_projected_points(self):
        plane_points = []
        for i in range(self.steps):
            y = 1 - i / (self.steps - 1)
            for e in range(self.dim):
                x = 1 - (e + 1) / self.dim
                plane_points.append([x, y])
        return plane_points
    

    def texturize(self, texture_file_path):
        im = cv2.imread(texture_file_path)
        height, width, _ = im.shape

        plane_mesh_points = self.plane_projected_points()

        self.texture = []
        for x, y in plane_mesh_points:
            vertex_color = im[int(y * (height-1))][int(x * width)]
            self.texture.append([
                vertex_color[2] / 255,
                vertex_color[1] / 255,
                vertex_color[0] / 255
            ])
    

    def visualize(self, polywindow = None):
        if polywindow:
            self.visualize_aux(polywindow)
        else:
            ps.init()
            self.visualize_aux(ps)
            ps.show()


    def visualize_aux(self, polywindow):
        projection_mesh = polywindow.register_surface_mesh("cylinder", np.array(self.points), np.array(self.faces), transparency=0.50)
        projection_mesh.set_smooth_shade(True)
        try:
            projection_mesh.add_color_quantity("mesh color", np.array(self.texture), enabled=True)
        except:
            pass
        polywindow.set_ground_plane_mode("none")