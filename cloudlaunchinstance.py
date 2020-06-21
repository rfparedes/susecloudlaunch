from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from pprint import pprint
from progress.spinner import Spinner
from constants import *
import json
import boto3


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
            # Contact AWS and get regions and azs
            regions_zones = self.get_aws_regions_azs()
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
        ]
        answers3 = prompt(questions3)

    def get_aws_regions_azs(self):
        """Get regions and AZs"""
        ec2 = boto3.client('ec2')

        spinner = Spinner('Talking to AWS ')

        regions_az = {}
        # Retrieves all regions/endpoints that work with EC2
        aws_regions = ec2.describe_regions()

        # Get a list of regions and then instantiate a new ec2 client for each
        # region in order to get list of AZs for the region
        for region in aws_regions['Regions']:
            spinner.next()
            my_region_name = region['RegionName']
            ec2_region = boto3.client(
                'ec2', region_name=my_region_name)
            my_region = [
                {'Name': 'region-name', 'Values': [my_region_name]}]
            aws_azs = ec2_region.describe_availability_zones(
                Filters=my_region)
            for az in aws_azs['AvailabilityZones']:
                zone = az['ZoneName']
                regions_az.setdefault(my_region_name, set()).add(zone)

        spinner.finish()
        return regions_az

    def get_aws_instance_types(self):
        """Get instance types per region"""
        ec2 = boto3.client('ec2')

        spinner = Spinner('Talking to AWS')

        instance_types = [instance_type['InstanceType']
                          for instance_type in ec2.describe_instance_types()['InstanceTypes']]

        return instance_types
