"""
This module contains global names

    root_dir
"""
# DEPENDENCIES
import os

# CUSTOM MODULES
import support

# GLOBAL VARIABLES
root_dir = os.path.dirname(__file__) # root directory, with all application elements
save_dir = os.path.abspath(os.path.join(root_dir, os.pardir, 'saved games'))
data_dir = os.path.abspath(os.path.join(root_dir, os.pardir, 'data'))
config_dict = support.loadJson(file_path=os.path.join(root_dir, 'game_config.json'))
save_file = r'wallet_state.json'
text_file = r'text.txt'

print('globals/paths: ', '\n\troot_dir: ', root_dir, '\n\tsave_dir: ', save_dir, '\n\tdata_dir: ', data_dir)
