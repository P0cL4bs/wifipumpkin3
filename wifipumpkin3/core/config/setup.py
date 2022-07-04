
import os
from distutils.dir_util import copy_tree
import wifipumpkin3.core.utility.constants as C
from sys import exit
from wifipumpkin3.core.utility.printer import (
    setcolor,
    display_messages,
)

def create_user_dir_config():
    user_config_dir = C.user_config_dir
    if not os.path.isdir(user_config_dir):
        print(
            display_messages(
                "creating config user dir on: {}".format(
                    setcolor(user_config_dir, color="orange")
                ),
                info=True,
            )
        )
        os.makedirs(user_config_dir, exist_ok=True)
        # force copy all files `config` to user_config_dir
        for folder in C.config_dir_packager_data:
            if os.path.isdir(folder):
                copy_tree(folder, user_config_dir + "/config")
                
        if os.path.isdir(user_config_dir):
            print(
                display_messages(
                    "the user config has been create {}, please restart the wp3!".format(
                        setcolor("sucessfully", color="green")
                    ),
                    sucess=True,
                )
            )
            exit(0)
        print(
            display_messages(
                "the user config has {} been created, please investigate!".format(
                    setcolor("not", color="red")
                ),
                error=True,
            )
        )
        exit(1)