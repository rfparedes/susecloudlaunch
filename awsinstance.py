from progress.spinner import Spinner
from constants import *
import boto3


class AWSInstance:

    def __init__(self, name):
        self.name = name

    def get_aws_regions_azs(self):
        """Get regions and AZs"""
        ec2 = boto3.client('ec2')

        spinner = Spinner('getting regions and azs from AWS ')

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

    def get_aws_images(self, os_version):
        """Get the images available"""
        ec2 = boto3.client('ec2')
        print(os_version)
        filters = [{
            'Name': 'name',
            'Values': ['*sles-sap-12-sp4*']
        }]

        spinner = Spinner('getting images from AWS ')
        aws_images = ec2.describe_images(Filters=filters)
        for image in aws_images['Images']:
            # spinner.next()
            print(image['Name'])
        # images = [image['Name']
        #         for image in ec2.describe_images()['Images']]
        # print(images)
        # return images
