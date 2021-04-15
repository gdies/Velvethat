# DEPENDENCIES
import json

# SUPPORT FUNCTIONS

def loadJson(file_path):
    """
    loads json serializable object
    file_path could be r'C:\Desktop\FILENAME.txt'
    """
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
    #return json.loads(json_obj) # converts string to python object
    return json_obj


def saveJson(obj, file_path):
    """
    saves json serializable object
    file_path could be r'C:\Desktop\FILENAME.txt'
    """
    with open(file_path, 'w') as file:
        json.dump(obj, file)
    return
