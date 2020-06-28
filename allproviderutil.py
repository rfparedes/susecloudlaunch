'''
Utilities for all providers
'''
from constants import *
from python_terraform import *
from progress.spinner import Spinner
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


def destroy_terraform_env(provider, projectid):
    tfvars_path = os.path.join(
        TF_APPLY_LOCATION, provider, projectid)
    tf = Terraform(
        working_dir=tfvars_path)
    spinner = Spinner(
        '\033[1;32;40m destroying ' + projectid + ' ')
    spinner.next()
    tf.destroy(capture_output=True)
    spinner.finish()
