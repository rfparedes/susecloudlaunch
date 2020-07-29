from constants import *
from python_terraform import *
from pathlib import *
from prompt_toolkit.validation import Validator, ValidationError
import os
import shutil
import threading
import time
import pickle


def cp_template(provider, envid):
    """create terraform folder for environment"""
    src_files = os.listdir(
        os.path.join(
            TF_TEMPLATE_LOCATION,
            provider))
    make_dir = os.path.join(TF_APPLY_LOCATION, provider, envid)
    os.makedirs(make_dir, exist_ok=True)
    for file_name in src_files:
        full_file_name = os.path.join(
            TF_TEMPLATE_LOCATION, provider, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(
                full_file_name,
                make_dir)

# --------------------------------------------------------------------


def get_terraform_project_dirs(provider):
    """Get directory names from tf_apply to provide to user when selecting which project to destroy"""
    # project_names = []
    tfvars_path = os.path.join(
        TF_APPLY_LOCATION, provider)
    project_names = os.listdir(tfvars_path)
    return project_names

# --------------------------------------------------------------------

# TODO : make this function asynchronous?
# TODO : need to show output


def destroy_terraform_env(provider, envid):
    """destroy a terraform environment"""
    print(WARNING + "This may take time and depends on provider" + ENDC)
    global done
    tfvars_path = os.path.join(
        TF_APPLY_LOCATION, provider, envid)
    tf = Terraform(
        working_dir=tfvars_path)
    done = False
    spin_thread = threading.Thread(target=spin_cursor)
    print(OKGREEN + 'Destroying ' + envid + ' ' + ENDC, end=" ")
    spin_thread.start()
    return_code, stdout, stderr = (tf.destroy(capture_output=True))
    done = True
    spin_thread.join()
    if return_code == 1:
        print()
        print(stderr)
        print(FAIL +
              "Destroy failed. Manually deleting the environment directory " +
              tfvars_path + ENDC)
    else:
        print()
        print(OKGREEN + "Destroy successful." + ENDC)
        # cleanup by deleting the directory
        shutil.rmtree(tfvars_path)

# --------------------------------------------------------------------


def create_terraform_tfvars(
        provider, region, zone, instance_type, imageid, instance, projectid):
    """create environment using terraform"""
    # Get logged in users public key type and key
    pubkey_type, pubkey = get_public_key()

    # TODO : for key pairs, use the ~/.ssh/id_rsa.pub as the default
    # keypair so whatever use is running this program
    if provider == "aws":
        username = "ec2-user"
        """Create the tfvars file with instance data"""
        template = """
        # AWS Settings
        aws_region_1        =  "{aws_region_1}"
        aws_zone_1          =  "{aws_zone_1}"
        aws_profile_1       =  "default"
        aws_key_pair_1      = "{pubkeytype} {pubkey} ec2-user"
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
            "app_name_1": instance,
            "pubkeytype": pubkey_type,
            "pubkey": pubkey
        }

    elif provider == "azure":
        username = "azure-user"
        """Create tfvars file with instance data"""
        template = """
        # Azure Settings
        azure_region_1        = "{azure_region_1}"
        azure_key_pair_1      = "{pubkeytype} {pubkey} {username}"
        azure_instance_type_1 = "Standard_{azure_instance_type_1}"
        azure_image_offer     = "{azure_image_offer}"
        azure_image_sku       = "{azure_image_sku}"
        azure_image_version   = "{azure_image_version}"

        private_vpc_cidr_1    = "{private_vpc_cidr_1}"
        private_subnet_cidr_1 = "{private_subnet_cidr_1}"


        # Application Definition
        app_name_1        = "{app_name_1}"
        """

        # Split the uri image into individual
        # publisher/offer/sku/version
        context = {
            "azure_region_1": region,
            "azure_instance_type_1": instance_type,
            "azure_image_offer": imageid.split(':')[1],
            "azure_image_sku": imageid.split(':')[2],
            "azure_image_version": imageid.split(':')[3],
            "app_name_1": instance,
            "private_vpc_cidr_1": PRIVATE_VPC_CIDR_1,
            "private_subnet_cidr_1": PRIVATE_SUBNET_CIDR_1,
            "pubkeytype": pubkey_type,
            "pubkey": pubkey,
            "username": username
        }

    elif provider == "gcp":
        username = "gce-user"
        """Create tfvars file with instance data"""
        template = """
        # GCP Settings
        gcp_region_1          = "{gcp_region_1}"
        gcp_zone_1            = "{gcp_zone_1}"
        gcp_project_1         = "{gcp_project_1}"
        ssh_keys              = "{username}:{pubkeytype} {pubkey} {username}"
        gcp_machine_type_1    = "{gcp_machine_type_1}"
        gcp_image_1           = "{gcp_image_1}"
        private_subnet_cidr_1 = "{private_subnet_cidr_1}"
        gcp_env_1             = "{gcp_env_1}"
        """
        context = {
            "gcp_region_1": region,
            "gcp_zone_1": zone,
            "gcp_project_1": projectid,
            "gcp_machine_type_1": instance_type,
            "gcp_image_1": imageid,
            "private_subnet_cidr_1": PRIVATE_SUBNET_CIDR_1,
            "pubkeytype": pubkey_type,
            "pubkey": pubkey,
            "username": username,
            "gcp_env_1": instance
        }

    global done
    tfvars_path = os.path.join(
        TF_APPLY_LOCATION, provider, instance)
    with open(os.path.join(tfvars_path, "terraform.tfvars"), 'w') as myfile:
        myfile.write(template.format(**context))

    tf = Terraform(
        working_dir=tfvars_path)
    done = False
    spin_thread = threading.Thread(target=spin_cursor)
    print(
        OKGREEN +
        "Creating " +
        instance +
        " in " +
        provider.upper() +
        ' ' +
        ENDC,
        end=" ")
    spin_thread.start()
    tf.init(capture_output=True)
    tf.plan(capture_output=True)
    return_code, stdout, stderr = tf.apply(
        skip_plan=True, capture_output=True)
    done = True
    spin_thread.join()
    if return_code == 1:
        print()
        print(FAIL + "Deployment failed." + ENDC)
        print(FAIL + stderr + ENDC)
        print(WARNING + "Rolling back." + ENDC)
        destroy_terraform_env(provider, instance)

    else:
        print()
        print(OKGREEN + "Deployment successful." + ENDC)
        my_ip = (tf.cmd("output", "ip"))
        print(OKBLUE + "ssh " + username + "@" + my_ip[1] + ENDC)

# --------------------------------------------------------------------


def spin_cursor():
    """https://stackoverflow.com/questions/48854567/python-asynchronous-progress-spinner"""
    global done
    while True:
        for cursor in '|/-\\':
            sys.stdout.write(cursor)
            sys.stdout.flush()
            time.sleep(0.1)  # adjust this to change the speed
            sys.stdout.write('\b')
            if done:
                return

# --------------------------------------------------------------------


def get_public_key():
    """Get public key of logged in user"""
    pubkey_path = str(Path.home()) + "/.ssh/id_rsa.pub"
    f = open(pubkey_path, "r")
    key_type, key, user = f.read().split()
    return key_type, key

# --------------------------------------------------------------------


def cache_write_data(filename, data):
    """Cache CSP object"""
    f = open(filename, "wb")
    pickle.dump(data, f)
    f.close()

# --------------------------------------------------------------------


def cache_read_data(filename):
    """Read CSP object from cache"""
    data = pickle.load(open(filename, "rb"))
    # Should cache be invalidated?
    current_time = time.time()
    creation_time = os.path.getctime(filename)
    if (current_time - creation_time) // (24 *
                                          3600) >= CACHE_INVALIDATE_DAYS:
        os.unlink(filename)
    return data

# --------------------------------------------------------------------


class EnvNameValidator(Validator):
    """ For userinterface input validator """

    def validate(self, document):
        """Validate the env name, must have 6 characters or more"""
        if len(document.text) >= 6:
            return True
        else:
            raise ValidationError(
                message='Name must be 6 characters or more',
                cursor_position=len(
                    document.text))

# --------------------------------------------------------------------
