'''
Utilities for all providers
'''
from constants import *
import os
import shutil


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
