from __future__ import print_function, unicode_literals
from PyInquirer import prompt
from pprint import pprint
import json
import boto3


class CloudLaunchInstance:

    def __init__(self, name):
        self.name = name

    # Provide terminal user interface to get user prompts and
    # preferences
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
        # self.get_aws_regions_azs()
        # self.get_aws_azs("us-west-1")
        self.get_aws_info()

    # get aws region list available
    def get_aws_regions(self):

        ec2 = boto3.client('ec2')
        regions = [region['RegionName']
                   for region in ec2.describe_regions()['Regions']]
        print(regions)

    # get aws availability zones list
    def get_aws_azs(self, region):

        region = "us-east-1"
        ec2 = boto3.client('ec2')
        azs = [az['ZoneName']
               for az in ec2.describe_availability_zones(Filters=region - name)['AvailabilityZones']]
        print(azs)

    def get_aws_info(self):
        ec2 = boto3.client('ec2')

        regions_az = {}
        # Retrieves all regions/endpoints that work with EC2
        aws_regions = ec2.describe_regions()

        # Get a list of regions and then instantiate a new ec2 client for each
        # region in order to get list of AZs for the region
        for region in aws_regions['Regions']:
            my_region_name = region['RegionName']
            ec2_region = boto3.client(
                'ec2', region_name=my_region_name)
            my_region = [
                {'Name': 'region-name', 'Values': [my_region_name]}]
            print("Current Region is %s" % my_region_name)
            aws_azs = ec2_region.describe_availability_zones(
                Filters=my_region)
            for az in aws_azs['AvailabilityZones']:
                zone = az['ZoneName']
                regions_az.setdefault(my_region_name, set()).add(zone)
