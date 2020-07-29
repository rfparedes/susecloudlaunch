from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json, Separator, style_from_dict
from constants import *
from awsinstance import AWSInstance
from azureinstance import AzureInstance
from gcpinstance import GCPInstance
from allproviderutil import *
import sys


class CloudLaunchInstance:
    """Store user interface information"""

    def __init__(self, name):
        self.name = name

    # --------------------------------------------------------------------
    def user_interface(self):
        """ Provide terminal user interface to get user prompts and preferences """

        print(
            OKGREEN + 'susecloudlaunch - Launch SLE instance on AWS,Azure,GCP' + ENDC)
        # Ask user first set of questions
        purpose_options = ['create', 'destroy']
        questions = [
            {
                'type': 'list',
                'name': 'purpose',
                'message': 'create or destroy instance & environment',
                'choices': purpose_options,
            },
            {
                'type': 'list',
                'name': 'provider',
                'message': 'on what provider',
                'choices': PROVIDERS,
            },
        ]

        answers = prompt(questions)

        # User interface when they want to create an instance
        if answers["purpose"] == "create":

            # TODO: Minimum 6 character project name
            # TODO: Check if project name is already used currently
            envid_creation = [
                {
                    'type': 'input',
                    'name': 'envid',
                    'message': 'unique environment name (min 6 chars)',
                    'default': '',
                    'validate': EnvNameValidator
                },
            ]
            envid_answer = prompt(envid_creation)

            if answers["provider"] == "aws":
                # create AWS instance object
                instance = AWSInstance(
                    envid_answer["envid"],
                    "aws",
                    "us-east-1",
                    "us-east-1a",
                    "t3.micro",
                    "ami-0",
                    "projectid")
                # Contact AWS and get regions and azs
                regions_zones = instance.get_aws_regions_azs()
                instance_type = AWS_INSTANCE_TYPES
                region_choices = sorted(regions_zones.keys())

            elif answers["provider"] == "azure":
                # create Azure instance object
                instance = AzureInstance(
                    envid_answer["envid"],
                    "azure",
                    "eastus",
                    "1",
                    "Standard_B1s",
                    "ami-0",
                    "projectid")
                region_choices = instance.get_azure_regions_azs()
                instance_type = AZURE_INSTANCE_TYPES
                regions_zones = 1

            elif answers["provider"] == "gcp":
                # create GCP instance object
                instance = GCPInstance(
                    envid_answer["envid"],
                    "gcp",
                    "us-east1",
                    "us-east1-b",
                    "f1.micro",
                    "ami-0",
                    "projectid")
                # Get GCP project names
                project_names = []
                project_names = instance.get_gcp_projects()
                existing_project_q = [
                    {
                        'type': 'list',
                        'name': 'gcp_project',
                        'message': 'pick GCP project to deploy in',
                        'choices': project_names,
                    },
                ]
                existing_project_a = prompt(existing_project_q)
                instance.set_projectid(
                    existing_project_a["gcp_project"])

                region_choices, gcp_zones = instance.get_gcp_regions()
                instance_type = GCP_INSTANCE_TYPES

            else:
                sys.exit("No provider selected")

            # Ask for a region based on provider
            questions2 = [
                {
                    'type': 'list',
                    'name': 'region',
                    'message': 'what region',
                    'choices': region_choices,
                }
            ]
            answers2 = prompt(questions2)
            instance.set_region(answers2['region'])
            # Ask for a zone based on region
            if answers["provider"] == "aws":
                questions3 = [
                    {
                        'type': 'list',
                        'name': 'zone',
                        'message': 'what zone',
                        'choices': sorted(regions_zones[answers2["region"]]),
                    },
                ]
            elif answers["provider"] == "azure":
                questions3 = [
                    {
                        'type': 'list',
                        'name': 'zone',
                        'message': 'what zone',
                        'choices': '1',
                    },
                ]
            elif answers["provider"] == "gcp":
                zone_choices = instance.get_gcp_zones(
                    answers2["region"], gcp_zones)
                questions3 = [
                    {
                        'type': 'list',
                        'name': 'zone',
                        'message': 'what zone',
                        'choices': zone_choices,
                    },
                ]
            questions3b = [
                {
                    'type': 'list',
                    'name': 'instance_type',
                    'message': 'what type',
                    'choices': instance_type,
                },
                {
                    'type': 'list',
                    'name': 'sles_or_sap',
                    'message': 'sles or sles-sap',
                    'choices': OS_TYPES,
                },
            ]

            answers3 = prompt(questions3)
            answers3b = prompt(questions3b)
            instance.set_zone(answers3['zone'])
            instance.set_instance_type(answers3b['instance_type'])

            if answers3b["sles_or_sap"] == "sles":
                questions4 = [
                    {
                        'type': 'list',
                        'name': 'os',
                        'message': 'os',
                        'choices': SLES_VERSIONS,
                    },
                ]

            elif answers3b["sles_or_sap"] == "sles-sap":
                questions4 = [
                    {
                        'type': 'list',
                        'name': 'os',
                        'message': 'os',
                        'choices': SLES_SAP_VERSIONS,
                    },
                ]
            answers4 = prompt(questions4)

            # handle OS version logic
            if answers["provider"] == "aws":
                images = instance.get_aws_images(answers4["os"])
                # image_names = instance.get_aws_image_names(images)
                image_dict = instance.get_aws_image_dict(images)
                # Exit if no images
                if not image_dict:
                    sys.exit(
                        "\033[1;32;40m No AWS images for this OS. Exiting")
                questions5 = [
                    {
                        'type': 'list',
                        'name': 'image',
                        'message': 'what image',
                        'choices': image_dict.values(),
                    },
                ]
                answers5 = prompt(questions5)
                image_id = (
                    list(
                        image_dict.keys())[
                        list(
                            image_dict.values()).index(
                            answers5["image"])])
                instance.set_ami(image_id)

            elif answers["provider"] == "azure":
                all_azure_images = instance.get_all_azure_images()
                images = instance.get_azure_images(
                    all_azure_images, answers4["os"], answers3b["sles_or_sap"])
                # Exit if no images
                if not images:
                    sys.exit(
                        "\033[1;32;40m No Azure images for this OS. Exiting")
                questions5 = [
                    {
                        'type': 'list',
                        'name': 'image',
                        'message': 'what image',
                        'choices': images,
                    },
                ]
                answers5 = prompt(questions5)
                instance.set_ami(answers5["image"])

            elif answers["provider"] == "gcp":
                images = instance.get_gcp_images(
                    answers3b["sles_or_sap"], answers4["os"])
                if not images:
                    sys.exit(
                        "\033[1;32;40m No GCP images for this OS. Exiting")
                questions5 = [
                    {
                        'type': 'list',
                        'name': 'image',
                        'message': 'what image',
                        'choices': images,
                    },
                ]
                answers5 = prompt(questions5)
                if answers3b["sles_or_sap"] == "sles-sap":
                    instance.set_ami(
                        "projects/suse-sap-cloud/global/images/" +
                        answers5["image"])
                elif answers3b["sles_or_sap"] == "sles":
                    instance.set_ami(
                        "projects/suse-cloud/global/images/" +
                        answers5["image"])

            questions6 = [
                {
                    'type': 'confirm',
                    'name': 'confirm',
                    'message': 'Create the environment now: ',
                    'default': True,
                },
            ]
            answers6 = prompt(questions6)
            if (answers6["confirm"]) == True:
                # Prepare tf apply directory
                cp_template(
                    instance.get_provider(), instance.get_instance())

                create_terraform_tfvars(
                    instance.get_provider(),
                    instance.get_region(),
                    instance.get_zone(),
                    instance.get_instance_type(),
                    instance.get_image(),
                    instance.get_instance(),
                    instance.get_projectid())

            else:
                sys.exit("\033[1;32;40m Exiting")

        # User interface when they want to destroy interface
        elif answers["purpose"] == "destroy":

            # Get current projects that can be destroyed
            project_names = get_terraform_project_dirs(
                answers["provider"])

            # No projects ever created so exit
            if not project_names:
                sys.exit(
                    WARNING + "No projects to destroy. Exiting" + ENDC)
            else:
                envid_select = [
                    {
                        'type': 'list',
                        'name': 'envid_destroy',
                        'message': 'what environment to destroy',
                        'choices': project_names,
                    },
                ]

                envid_destroy_answer = prompt(envid_select)

                destroy_confirm = [
                    {
                        'type': 'confirm',
                        'name': 'destroy_confirm',
                        'message': 'Are you sure: ',
                        'default': False,
                    },
                ]
                destroy_answer = prompt(destroy_confirm)
                if destroy_answer['destroy_confirm'] == True:
                    destroy_terraform_env(
                        (answers["provider"]), envid_destroy_answer["envid_destroy"])
                else:
                    sys.exit("Not destroying. Exiting")
