import os
import json
import math
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import numpy

current_directory = os.getcwd()
data_folder_path = "data"
folder_path = os.path.join(current_directory, data_folder_path)

dicts = []
names = []
for file_name in os.listdir(folder_path):
    path = os.path.join(folder_path, file_name)
    for sub_file in os.listdir(path):
        if "desc" in sub_file:
            with open(os.path.join(path, sub_file), "r") as file:
                dicts.append(json.load(file))
                names.append(sub_file.split("/")[-1][0:4])


points = []
for obj_dict in dicts:
    for arch_id in obj_dict:
        keys = list(obj_dict[arch_id].keys())
        x = 0
        y = 0
        for i in range(len(obj_dict[arch_id])):
            key = keys[i]
            val = obj_dict[arch_id][key]
            x += val * math.cos(i * math.pi / 8)
            y += val * math.sin(i * math.pi / 8)
        points.append([x, y])

print(dicts)

points_array = numpy.array(points)

plt.scatter(points_array[:, 0], points_array[:, 1])
print(len(points_array))
plt.title(f"Distribución de elementos")
plt.show()

n_d = 3
e_d = 0.035
db = DBSCAN(eps=e_d, min_samples=n_d).fit(points_array)
labels = db.labels_


n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
n_noise_ = list(labels).count(-1)

print("Estimated number of clusters: %d" % n_clusters_)
print("Estimated number of noise points: %d" % n_noise_)

unique_labels = set(labels)
core_samples_mask = numpy.zeros_like(labels, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True


clasification = {}

point_id = 0
for obj_dict in range(len(dicts)):
    for arch_id in dicts[obj_dict]:
        if not labels[point_id] in clasification:
            clasification[labels[point_id]] = {}
        clasification[labels[point_id]][(names[obj_dict], arch_id)] = (point_id, points[point_id])
        point_id += 1

for key in clasification:
    print(f"Cluster {key}")
    for sub_key in clasification[key]:
        print(sub_key, clasification[key][sub_key])


colors = [plt.cm.Spectral(each) for each in numpy.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        col = [0, 0, 0, 1]

    class_member_mask = labels == k

    xy = points_array[class_member_mask]
    plt.plot(
        xy[:, 0],
        xy[:, 1],
        "o",
        markerfacecolor=tuple(col),
        markeredgecolor="k",
        markersize=5,
    )

plt.title(f"Número de clusters: {n_clusters_}           n = {n_d}, e = {e_d}")
plt.show()