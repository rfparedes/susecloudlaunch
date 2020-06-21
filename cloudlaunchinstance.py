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
            instance = AWSInstance("instance-1")
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
                'name': 'os',
                'message': 'os',
                'choices': OS_VERSIONS
            },
        ]
        answers3 = prompt(questions3)

        # handle OS version logic
        instance.get_aws_images(answers3["os"])
