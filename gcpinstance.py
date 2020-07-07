from oauth2client.client import GoogleCredentials
from constants import *
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from google.cloud import resource_manager
from googleapiclient import discovery
from pprint import pprint


class GCPInstance:

    def __init__(self, name, provider, region,
                 zone, instance_type, imageid):
        self._instance = name
        self._provider = provider
        self._region = region
        self._zone = zone
        self._instance_type = instance_type
        self._imageid = imageid

    def __str__(self):
        return 'AWSInstance(name=' + self._instance + ', provider=' + self._provider + ', region=' + self._region + ', zone=' + \
            self._zone + ', type=' + self._instance_type + \
            ', imageid=' + self._imageid + ')'

    def get_instance(self):
        """Return name of instance"""
        return self._instance

    def set_instance(self, instance):
        """Set name of instance"""
        self._instance = instance

    def get_provider(self):
        """Return name of provider"""
        return self._provider

    def set_provider(self, provider):
        """Set name of provider"""
        self._provider = provider

    def get_region(self):
        """Return name of region"""
        return self._region

    def set_region(self, region):
        """Set region of instance"""
        self._region = region

    def get_zone(self):
        """Return name of zone"""
        return self._zone

    def set_zone(self, zone):
        """Set name of zone"""
        self._zone = zone

    def get_instance_type(self):
        """Get the instance type"""
        return self._instance_type

    def set_instance_type(self, instance_type):
        """Set the instance type"""
        self._instance_type = instance_type

    def get_image(self):
        """Return image id"""
        return self._imageid

    def set_ami(self, imageid):
        """Set ami id of instance"""
        self._imageid = imageid

    def create_gcp_project(self, projectid):
        client = resource_manager.Client()
        new_project = client.new_project(projectid, name=projectid)
        new_project.create()

    def get_gcp_regions(self):
        """Get GCP available regions"""
        ComputeEngine = get_driver(Provider.GCE)
        # TODO: dynamically get client_id and client_secret from
        # ~/.config/gcloud/application_default_credentials.json
        driver = ComputeEngine(
            '764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com',
            'd-FL95Q19q7MQmFpd7hHD0Ty',
            project=self.get_instance(),
            datacenter='us-east1-b')
        regions = []
        for region in driver.ex_list_regions():
            regions.append(region.name)
        return regions

    def get_gcp_zones(self, region):
        """Get GCP Zones for a region"""
        ComputeEngine = get_driver(Provider.GCE)
        driver = ComputeEngine(
            '764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com',
            'd-FL95Q19q7MQmFpd7hHD0Ty',
            project=self.get_instance(),
            datacenter='us-east1-b')
        region_zones = []
        for zone in driver.ex_list_zones():
            if region in zone.name:
                region_zones.append(zone.name)
        return region_zones

    def get_gcp_images(self):
        ComputeEngine = get_driver(Provider.GCE)
        driver = ComputeEngine(
            '764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com',
            'd-FL95Q19q7MQmFpd7hHD0Ty',
            project=self.get_instance(),
            datacenter='us-east1-b')
        print(driver.list_images())
