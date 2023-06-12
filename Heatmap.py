import numpy as np
import math
from sklearn.neighbors import kneighbors_graph
from PIL import Image
import json
import os


class Line:
    def __init__(self, A, B):
        num = B[1] - A[1]
        den = B[0] - A[0]
        try:
            m = num / den
        except:
            m = 1000
        self.A = A
        self.B = B
        self.alpha = m
        self.beta = - 1
        self.gamma = - (m * A[0] - A[1])


    def distance2point(self, point):
        if not ((self.A[0] < point[0] < self.B[0]) or (self.B[0] < point[0] < self.A[0])):
            if not ((self.A[1] < point[1] < self.B[1]) or (self.B[1] < point[1] < self.A[1])):
                return 100
        a = self.alpha * point[0]
        b = self.beta * point[1]
        num = abs(a + b + self.gamma)
        den = math.sqrt(self.alpha ** 2 + self.beta ** 2)
        return num / den


    def __eq__(self, line):
        p1_1c = self.A[0] == line.A[0] or self.A[0] == line.B[0]
        p1_2c = self.A[1] == line.A[1] or self.A[1] == line.B[1]
        p2_1c = self.B[0] == line.B[0] or self.B[0] == line.A[0]
        p2_2c = self.B[1] == line.B[1] or self.B[1] == line.A[1]
        return p1_1c and p1_2c and p2_1c and p2_2c


    def intersect(self, line):
        try:
            x_intersection = (self.gamma - line.gamma) / (line.alpha - self.alpha)
        except:
            return False
        if (self.A == line.A or self.B == line.A or self.B == line.A or self.B == line.B):
            return False
        y_intersection = self.gamma + self.alpha * x_intersection
        cond_1 = (self.A[0] < x_intersection < self.B[0]) or (self.B[0] < x_intersection < self.A[0])
        cond_2 = (self.A[1] < y_intersection < self.B[1]) or (self.B[1] < y_intersection < self.A[1])
        return cond_1 and cond_2



class Heatmap:
    def __init__(self, name, path, points, radius = 25, dimention = 100):
        self.name = name
        self.path = path
        self.colors = [(1,0,0),(0,1,0),(0,0,1),(1,0,1),(1,1,0),(0,1,1),(1,1,1)]
        self.radius = radius
        self.dimention = dimention
        self.intensity = None
        self.image = None
        self.X = []
        self.Y = []
        self.lines = None
        self.lines_intensity = None
        for point_list in points:
            sub_x = []
            sub_y = []
            reflected_points = []
            for x, y, z in point_list:
                new_x = math.acos(x)
                if (z < 0):
                    new_x = 2 * math.pi - new_x
                if (new_x > math.pi):
                    reflected_points.append([int((new_x - 2 * math.pi)*self.dimention), int((y+1)*self.dimention)])
                else:
                    reflected_points.append([int((2 * math.pi + new_x)*self.dimention), int((y+1)*self.dimention)])
                sub_y.append(int((y+1) * self.dimention))
                sub_x.append(int(new_x * self.dimention))
            for x, y in reflected_points:
                sub_x.append(x) 
                sub_y.append(y)
            self.X.append(sub_x)
            self.Y.append(sub_y)

        self.lines = []

        every_point = []
        for i in range(len(self.X)):
            for j in range(len(self.X[i])):
                every_point.append([self.X[i][j], self.Y[i][j]])

        try:
            matrix = kneighbors_graph(every_point, 4)
        except:
            matrix = kneighbors_graph(every_point, len(every_point)-1)
        conectivity_array = matrix.toarray()
        e = 0

        descs = []

        for i in range(len(self.X)):
            lines = []
            desc = {
                0: 0,
                45: 0,
                90: 0,
                135: 0,
                180: 0,
                225: 0,
                270: 0,
                315: 0
            }
            for j in range(len(self.X[i])):
                con = conectivity_array[e]
                for r in range(len(con)):
                    if con[r] == 1:
                        line = Line(every_point[r], every_point[e])
                        if not line in lines:
                            lines.append(line)
                        vect_x = every_point[r][0] - every_point[e][0]
                        vect_y = every_point[r][1] - every_point[e][1]
                        mod = (vect_x ** 2 + vect_y ** 2) ** 0.5
                        try:
                            norm_x = vect_x / mod
                        except:
                            continue

                        angle_rad = math.acos(norm_x)
                        if vect_y < 0:
                            angle_rad += 2 * (math.pi - angle_rad)
                        angle_deg = angle_rad * 180 / math.pi
                        eq_class = int(((angle_deg + 45 / 2) // 45) * 45)
                        if eq_class == 360:
                            eq_class = 0
                        desc[eq_class] += 1

                e += 1
            descs.append(desc)
            self.lines.append(lines)

        for desc in descs:
            tot = sum(list(desc.values()))
            for key in desc:
                desc[key] /= tot
        
        json_desc = {}
        for i in range(len(descs)):
            json_desc[i] = descs[i]

        json_object = json.dumps(json_desc, indent=4)

        with open(f"{path}/{name}_descriptor.json", "w") as json_file:
            json_file.write(json_object)
    

    def ponder(self, distance, radius = 0):
        if radius <= 0:
            considered_radius = self.radius
        else:
            considered_radius = radius
        magnitude = distance / considered_radius
        value = (1 - magnitude ** 1.25) ** 1.8
        return value


    def generate_heatmap(self):
        x_grid = np.arange(0,int(2 * math.pi * self.dimention), 1)
        y_grid = np.arange(0,int(2 * self.dimention), 1)
        x_mesh, y_mesh = np.meshgrid(x_grid,y_grid)
        if self.intensity != None:
            return
        self.intensity = []
        for id in range(len(self.X)):
            intensity_list = []
            x = self.X[id]
            y = self.Y[id]
            for j in range(len(x_mesh)):
                intensity_row = []
                for k in range(len(x_mesh[0])):
                    value_list = []
                    for i in range(len(x)):
                        distance = math.sqrt((x_mesh[j][k]-x[i])**2+(y_mesh[j][k]-y[i])**2) 
                        if distance <= self.radius:
                            value = self.ponder(distance)
                        else:
                            value = 0
                        value_list.append(value)
                    total_value = sum(value_list)
                    intensity_row.append(total_value)
                intensity_list.append(intensity_row)
            self.intensity.append(intensity_list)


    def generate_lines(self):
        x_grid = np.arange(0,int(2 * math.pi * self.dimention), 1)
        y_grid = np.arange(0,int(2 * self.dimention), 1)
        x_mesh, y_mesh = np.meshgrid(x_grid,y_grid)
        if self.lines_intensity != None:
            return
        self.lines_intensity = []
        for i in range(len(self.lines)):
            lines_intensity = []
            for j in range(len(x_mesh)):
                intensity_list = []
                for k in range(len(x_mesh[0])):
                    value_list = []
                    for line in self.lines[i]:
                        distance = line.distance2point([x_mesh[j][k], y_mesh[j][k]])
                        if distance <= 1.2:
                            value = self.ponder(distance, 1.2)
                        else:
                            value = 0
                        value_list.append(value)
                    total_value = sum(value_list)
                    intensity_list.append(total_value)
                lines_intensity.append(intensity_list)
            self.lines_intensity.append(lines_intensity)


    def generate_image(self):
        if self.intensity == None:
            self.generate_heatmap()
            self.generate_lines()
        self.image = Image.new("RGB", (int(math.pi * 2 * self.dimention), 2 * self.dimention), color = "black")
        for n in range(len(self.intensity)):
            heatmap = self.intensity[n]
            cr, cg, cb = self.colors[n]
            chr, chg, chb = self.colors[-(n+1)]
            lines_intensity = self.lines_intensity[n]
            chr, chg, chb = self.colors[-(n+1)]   
            for i in range(int(math.pi * 2 * self.dimention)):
                for j in range(2 * self.dimention):
                    r, g, b = self.image.getpixel((int(math.pi * 2 * self.dimention) - 1 - i, 2 * self.dimention - 1 - j))
                    in_r = int(heatmap[j][i]*255*cr)
                    in_g = int(heatmap[j][i]*255*cg)
                    in_b = int(heatmap[j][i]*255*cb)
                    inl_r = int(lines_intensity[j][i]*255*chr)
                    inl_g = int(lines_intensity[j][i]*255*chg)
                    inl_b = int(lines_intensity[j][i]*255*chb)
                    self.image.putpixel((int(math.pi * 2 * self.dimention) - 1 - i, 2 * self.dimention - 1 - j), (in_r+inl_r+r,in_g+inl_g+g,in_b+inl_b+b))
        self.image.save(os.path.join(self.path, f"{self.name}_heatmap.png"))
        return self.image