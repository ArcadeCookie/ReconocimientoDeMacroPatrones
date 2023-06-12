import os
from StructureReader import StructureReader

deep = True
render = False
process = True

current_directory = os.getcwd()
data_folder_path = "data"
folder_path = os.path.join(current_directory, data_folder_path)

for file_name in os.listdir(folder_path):
    path = os.path.join(folder_path, file_name)
    print(f"doing {file_name}")
    StructureReader(path, deep, render, process).CreatePolyscopeObject()
