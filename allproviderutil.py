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
    # project_names = []
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


def create_terraform_tfvars(
        provider, region, zone, instance_type, imageid, instance):

    if provider == "aws":
        """Create the tfvars file with instance data"""
        template = """
        # AWS Settings
        aws_region_1        =  "{aws_region_1}"
        aws_zone_1          =  "{aws_zone_1}"
        aws_profile_1       =  "default"
        aws_key_pair_1      = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8vQVGcwfKDT32QdWb9+PVVzAF1NVEUhOPmSbH7n8w2bIyGw7voUsEE9IdhmKr2qulnKJVRHd7XfEzBj0KJFTlkfSFEJHF/5TO4/oe4mEZkVE1H9XdnT8DsQ1Ytr+ewuRF9e5OKseQEZqPrINti4AzZ5McoS20McNNOiJCzzsn8n9NuJXBcnrBsmdj0wcJQodl3rV1v3w+rEuoosrTUqkoEn8wzySlSR3US9iYK6R/yeylVBJiPA5rCjox3SkAqsaxzfTaCNAfl5hOc+xRRU/+wIE0slro65HfwQDSJfqehJmeJ4EARInoxZabc061hVdLx2/JEIyawMvA/FDa2Qjd rich.paredes"
        aws_instance_type_1 =  "{aws_instance_type_1}"
        aws_ami_1           =  "{aws_ami_1}"

        # AWS Network
        private_vpc_cidr_1    = "192.168.0.0/16"
        private_subnet_cidr_1 = "192.168.111.0/24"

        # Application Definition
        app_name_1        = "{app_name_1}"
        app_environment_1 = "test"
        """
        context = {
            "aws_region_1": region,
            "aws_zone_1": zone,
            "aws_instance_type_1": instance_type,
            "aws_ami_1": imageid,
            "app_name_1": instance
        }
        tfvars_path = os.path.join(
            TF_APPLY_LOCATION, "aws", instance)
        with open(os.path.join(tfvars_path, "terraform.tfvars"), 'w') as myfile:
            myfile.write(template.format(**context))

        tf = Terraform(
            working_dir=tfvars_path)
        tf.init(capture_output=False)
        tf.plan(capture_output=False)
        tf.apply(skip_plan=True, capture_output=True)
        my_ip = (tf.cmd("output", "ip"))
        print("\033[1;32;40m ssh ec2-user@" + my_ip[1])


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
