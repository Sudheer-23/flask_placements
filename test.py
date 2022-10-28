import os
  
# Get the list of all files and directories
# in the root directory
path = "C:/Sudheer/flask_custom_mails/static/attachments"
dir_list = os.listdir(path)
  
print("Files and directories in '", path, "' :") 
  
# print the list
print(dir_list)