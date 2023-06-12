import os
import polyscope as ps
from StructureReader import StructureReader

deep = False
render = True
process = True

current_directory = os.getcwd()
data_folder_path = "data"
folder_name = "0028"
folder_path = os.path.join(current_directory, data_folder_path, folder_name)

SR = StructureReader(folder_path, deep, render, process)
obj = SR.CreatePolyscopeObject()
obj.visualize()