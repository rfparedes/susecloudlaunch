from progress.spinner import Spinner
from constants import *
from collections import OrderedDict
from python_terraform import *
from allproviderutil import *
import boto3
import time
import os


class AWSInstance:
    """Store AWS instance information"""

    def __init__(self, name, provider, region,
                 zone, instance_type, imageid, projectid):
        self._instance = name
        self._provider = provider
        self._region = region
        self._zone = zone
        self._instance_type = instance_type
        self._imageid = imageid
        self._projectid = projectid

    # --------------------------------------------------------------------
    def __str__(self):
        return 'AWSInstance(name=' + self._instance + ', provider=' + self._provider + ', region=' + self._region + ', zone=' + \
            self._zone + ', type=' + self._instance_type + \
            ', imageid=' + self._imageid + ', projectid=' + self._projectid + ')'

    # --------------------------------------------------------------------
    def get_instance(self):
        """Return name of instance"""
        return self._instance

    # --------------------------------------------------------------------
    def set_instance(self, instance):
        """Set name of instance"""
        self._instance = instance

    # --------------------------------------------------------------------
    def get_provider(self):
        """Return name of provider"""
        return self._provider

    # --------------------------------------------------------------------
    def set_provider(self, provider):
        """Set name of provider"""
        self._provider = provider

    # --------------------------------------------------------------------
    def get_region(self):
        """Return name of region"""
        return self._region

    # --------------------------------------------------------------------
    def set_region(self, region):
        """Set region of instance"""
        self._region = region

    # --------------------------------------------------------------------
    def get_zone(self):
        """Return name of zone"""
        return self._zone

    # --------------------------------------------------------------------
    def set_zone(self, zone):
        """Set name of zone"""
        self._zone = zone

    # --------------------------------------------------------------------
    def get_instance_type(self):
        """Get the instance type"""
        return self._instance_type

    # --------------------------------------------------------------------
    def set_instance_type(self, instance_type):
        """Set the instance type"""
        self._instance_type = instance_type

    # --------------------------------------------------------------------
    def get_image(self):
        """Return image id"""
        return self._imageid

    # --------------------------------------------------------------------
    def set_ami(self, imageid):
        """Set ami id of instance"""
        self._imageid = imageid

    # --------------------------------------------------------------------

    def get_projectid(self):
        """Return project id"""
        return self._projectid

    # --------------------------------------------------------------------
    def set_projectid(self, projectid):
        """Set projectid of instance"""
        self._projectid = projectid

    # --------------------------------------------------------------------

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
        spinner = Spinner(
            OKGREEN +
            "Getting images from AWS" +
            ' ' +
            ENDC,
            end=" ")
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
