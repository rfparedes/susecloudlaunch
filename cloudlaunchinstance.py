from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from constants import *
from awsinstance import AWSInstance

import json


class CloudLaunchInstance:

    def __init__(self, name):
        self.name = name

    def user_interface(self):
        """ Provide terminal user interface to get user prompts and preferences """
        # Ask user first set of questions
        purpose_options = ['create', 'destroy']
        questions = [
            {
                'type': 'list',
                'name': 'purpose',
                'message': 'create or destroy instance',
                'choices': purpose_options,
            },
            {
                'type': 'input',
                'name': 'projectid',
                'message': 'unique project name',
                'default': 'suse-repro-123',
            },
            {
                'type': 'list',
                'name': 'provider',
                'message': 'on what provider',
                'choices': PROVIDERS,
            },
        ]

        answers = prompt(questions)

        if answers["provider"] == "AWS":
            # create AWS instance object
            instance = AWSInstance(answers["projectid"]+"-instance", "us-east-1", "us-east-1a", "small", "ami-0")
            # Contact AWS and get regions and azs
            regions_zones = instance.get_aws_regions_azs()
            instance_type = AWS_INSTANCE_TYPES
        elif answers["provider"] == "Azure":
            pass
        elif answers["provider"] == "GCP":
            pass

        # Ask for a region based on provider
        questions2 = [
            {
                'type': 'list',
                'name': 'region',
                'message': 'what region',
                'choices': regions_zones.keys(),
            }
        ]
        answers2 = prompt(questions2)
        instance.set_region(answers2['region'])
        # Ask for a zone based on region
        questions3 = [
            {
                'type': 'list',
                'name': 'zone',
                'message': 'what zone',
                'choices': regions_zones[answers2["region"]],
            },
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
        instance.set_zone(answers3['zone'])
        instance.set_instance_type(answers3['instance_type'])

        if answers3["sles_or_sap"] == "sles":
            questions4 = [
                {
                    'type': 'list',
                    'name': 'os',
                    'message': 'os',
                    'choices': SLES_VERSIONS,
                },
            ]

        elif answers3["sles_or_sap"] == "sles for sap":
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

            questions5 = [
                {
                    'type': 'list',
                    'name': 'image',
                    'message': 'what image',
                    'choices': images,
                },
            ]

            for key,value in images.items():
                print (key)
                print (value['name'])


        # answers5 = prompt(questions5)

