from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from pprint import pprint
import json
import Boto


class CloudLaunchInstance:

    def __init__(self, name):
        self.name = name

    def user_interface(self):

        purpose_options = ['create', 'destroy']
        provider_options = ['AWS', 'Azure', 'GCP']
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
                'choices': provider_options,
            },
        ]
        answers = prompt(questions)
        pprint(answers)
        print(answers["projectid"])

    def get_aws_regions(self):
