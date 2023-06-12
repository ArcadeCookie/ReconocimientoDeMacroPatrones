import os
import json

def distance(dict1, dict2):
    print(dict1)
    dist = 0
    for key in dict1["0"]:
        dist += abs(dict1["0"][key] - dict2["0"][key])
    return dist

def distances(dicts, names):
    distances = {}
    for i in range(len(dicts)):
        dict = dicts[i]
        distances[names[i]] = {}
        distances_list = []
        for e in range(len(dicts)):
            dist = distance(dict, dicts[e])
            distances_list.append((dist, names[e]))
        distances[names[i]]["distances"] = distances_list
    return distances

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
    
d = distances(dicts, names)
json_object = json.dumps(d, indent=4)
with open("results.json", "w") as file:
    file.write(json_object)