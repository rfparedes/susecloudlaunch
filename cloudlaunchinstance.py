from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from constants import *
from awsinstance import AWSInstance
from azureinstance import AzureInstance
import json
import allproviderutil
import sys


class CloudLaunchInstance:

    def __init__(self, name):
        self.name = name

    def user_interface(self):
        """ Provide terminal user interface to get user prompts and preferences """

        print(
            '\033[1;32;40m susecloudlaunch - Launch SLE instance on AWS,Azure,GCP')
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

            projectid_creation = [
                {
                    'type': 'input',
                    'name': 'projectid',
                    'message': 'specify unique project name',
                    'default': 'suse-repro-123',
                },
            ]
            projectid_answer = prompt(projectid_creation)

            if answers["provider"] == "aws":
                # create AWS instance object
                instance = AWSInstance(
                    projectid_answer["projectid"],
                    "AWS",
                    "us-east-1",
                    "us-east-1a",
                    "small",
                    "ami-0")
                # Contact AWS and get regions and azs
                regions_zones = instance.get_aws_regions_azs()
                instance_type = AWS_INSTANCE_TYPES
                region_choices = sorted(regions_zones.keys())

            elif answers["provider"] == "azure":
                # create Azure instance object
                instance = AzureInstance(
                    projectid_answer["projectid"],
                    "Azure",
                    "eastus",
                    "1",
                    "Standard_B1s",
                    "ami-0")
                region_choices = instance.get_azure_regions_azs()
                instance_type = AZURE_INSTANCE_TYPES
                regions_zones = 1

            elif answers["provider"] == "gcp":
                pass

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
            if answers["provider"] == "AWS":
                questions3 = [
                    {
                        'type': 'list',
                        'name': 'zone',
                        'message': 'what zone',
                        'choices': sorted(regions_zones[answers2["region"]]),
                    },
                ]
            elif answers["provider"] == "Azure":
                questions3 = [
                    {
                        'type': 'list',
                        'name': 'zone',
                        'message': 'what zone',
                        'choices': '1',
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
                    'message': 'sles or sles for sap',
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

            elif answers3b["sles_or_sap"] == "sles for sap":
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
            if answers["provider"] == "AWS":
                images = instance.get_aws_images(answers4["os"])
                # image_names = instance.get_aws_image_names(images)
                image_dict = instance.get_aws_image_dict(images)
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
            print(image_id)
            instance.set_ami(image_id)

            questions6 = [
                {
                    'type': 'confirm',
                    'name': 'confirm',
                    'message': 'Create the environment now: ',
                    'default': True,
                },
            ]
            answers6 = prompt(questions6)

            # Prepare tf apply directory
            allproviderutil.cp_template(
                "aws", instance.get_instance())

            instance.create_terraform_tfvars()

        # User interface when they want to destroy interface
        elif answers["purpose"] == "destroy":

            # Get current projects that can be destroyed
            project_names = allproviderutil.get_terraform_project_dirs(
                answers["provider"])

            # No projects ever created so exit
            if not project_names:
                sys.exit(
                    '\033[1;32;40m No projects to destroy. Exiting')
            else:
                projectid_select = [
                    {
                        'type': 'list',
                        'name': 'projectid_destroy',
                        'message': 'what project to destroy',
                        'choices': project_names,
                    },
                ]

                projectid_destroy_answer = prompt(projectid_select)

                allproviderutil.destroy_terraform_env(
                    (answers["provider"]), projectid_destroy_answer["projectid_destroy"])

        else:
            sys.exit('Neither create or destroy.  Exiting.')
