'''
Utilities for all providers
'''
from constants import *
from python_terraform import *
import os
import shutil
import threading
import time


'''
Provider agnostic function to terraform template files to created project folder
'''


def cp_template(provider, projectid):
    src_files = os.listdir(
        os.path.join(
            TF_TEMPLATE_LOCATION,
            provider))
    make_dir = os.path.join(TF_APPLY_LOCATION, provider, projectid)
    os.makedirs(make_dir, exist_ok=True)
    for file_name in src_files:
        full_file_name = os.path.join(
            TF_TEMPLATE_LOCATION, provider, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(
                full_file_name,
                make_dir)


'''
Get directory names from tf_apply to provide to user when selecting which project to destroy
'''


def get_terraform_project_dirs(provider):
    #project_names = []
    tfvars_path = os.path.join(
        TF_APPLY_LOCATION, provider)
    project_names = os.listdir(tfvars_path)
    return project_names


'''
Provider agnostic function to destroy a terraform environment
'''


def destroy_terraform_env(provider, projectid):
    global done
    tfvars_path = os.path.join(
        TF_APPLY_LOCATION, provider, projectid)
    tf = Terraform(
        working_dir=tfvars_path)
    done = False
    spin_thread = threading.Thread(target=spin_cursor)
    print('\033[1;32;40m destroying ' + projectid + ' ', end=" ")
    spin_thread.start()
    tf.destroy(capture_output=True)
    done = True
    spin_thread.join()
    # cleanup by deleting the directory
    shutil.rmtree(tfvars_path)


'''
https://stackoverflow.com/questions/48854567/python-asynchronous-progress-spinner
'''


def spin_cursor():
    global done
    while True:
        for cursor in '|/-\\':
            sys.stdout.write(cursor)
            sys.stdout.flush()
            time.sleep(0.1)  # adjust this to change the speed
            sys.stdout.write('\b')
            if done:
                return
