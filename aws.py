from constants import *
from collections import OrderedDict
from instance import Instance
import boto3
import time
import os


class AWSInstance(Instance):
    """Store AWS instance information"""

    def get_aws_regions_azs(self):
        """Get regions and AZs"""
        ec2 = boto3.client('ec2')
        regions_az = {}
        if (not (os.path.isfile(REGION_CACHE_FILENAME + self.get_provider()))):
            spinner = Spinner(
                '\033[1;32;40m getting regions and azs from AWS ')
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
                    regions_az.setdefault(
                        my_region_name, set()).add(zone)
            # cache the results
            cache_write_data(
                REGION_CACHE_FILENAME +
                self.get_provider(),
                regions_az)
        else:
            regions_az = cache_read_data(
                REGION_CACHE_FILENAME + self.get_provider())

        return regions_az

    # --------------------------------------------------------------------
    def get_aws_instance_types(self):
        """Get instance types per region"""
        ec2 = boto3.client('ec2')
        spinner = Spinner('Talking to AWS')
        instance_types = [instance_type['InstanceType']
                          for instance_type in ec2.describe_instance_types()['InstanceTypes']]
        return instance_types

    # --------------------------------------------------------------------
    def get_aws_images(self, os_version):
        """Get the images available"""
        ec2 = boto3.client('ec2', self._region)
        os = "*" + os_version + '*'
        filters = [{
            'Name': 'name',
            'Values': [os]
        }]
        image_info = {}
        spinner = Spinner('\033[1;32;40m getting images from AWS ')
        aws_images = ec2.describe_images(Filters=filters)
        for image in aws_images['Images']:
            image_info[image['ImageId']] = {}
            image_info[image['ImageId']]['name'] = image['Name']
            image_info[image['ImageId']
                       ]['date'] = image['CreationDate']
        spinner.next()
        # Sort images by date
        sorted_images = dict(OrderedDict(
            sorted(
                image_info.items(),
                key=lambda t: t[1]['date'])))
        spinner.finish()
        return sorted_images

    # --------------------------------------------------------------------
    def get_aws_image_names(self, images):
        """Get just the aws image name into a list"""
        ami_list = []
        for key, value in images.items():
            ami_list.append(value['name'])
        return ami_list

    # --------------------------------------------------------------------
    def get_aws_image_dict(self, images):
        """Get just the aws image name into a list"""
        ami_dict = {}
        for key, value in images.items():
            ami_dict[key] = value['name']
        return ami_dict
