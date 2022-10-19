import os
  
# Get the list of all files and directories
# in the root directory
path = "attachments"
dir_list = os.listdir(path)
  
print("Files and directories in '", path, "' :") 
  
# print the list
print(dir_list)