from constants import *
from google.cloud import resource_manager
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import sys
from allproviderutil import *


class GCPInstance:
    """Store GCP instance information"""

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
    def get_gcp_projects(self):
        """Return list of projects in user account"""
        project_list = []
        # Filter on only the active projects
        env_filter = {'lifecycleState': 'ACTIVE'}
        client = resource_manager.Client()
        for project in client.list_projects(env_filter):
            project_list.append(project.project_id)
        return project_list

    # --------------------------------------------------------------------
    def get_gcp_regions(self):
        """Get GCP available regions and zones in one API call"""
        if (not (os.path.isfile(REGION_CACHE_FILENAME + self.get_provider()))):
            regions = []
            zones = []
            credentials = GoogleCredentials.get_application_default()
            service = discovery.build(
                'compute', 'v1', credentials=credentials)
            project = self.get_projectid()
            request = service.regions().list(project=project)
            while request is not None:
                response = request.execute()

                for region in response['items']:
                    regions.append(region['name'])
                    for zone in region['zones']:
                        zones.append(zone.rsplit('/', 1)[-1])
                request = service.regions().list_next(
                    previous_request=request, previous_response=response)
            # Cache regions and zones
            cache_write_data(
                REGION_CACHE_FILENAME +
                self.get_provider(), regions)
            cache_write_data(
                ZONE_CACHE_FILENAME +
                self.get_provider(),
                zones)

        else:
            regions = cache_read_data(REGION_CACHE_FILENAME +
                                      self.get_provider())
            zones = cache_read_data(
                ZONE_CACHE_FILENAME + self.get_provider())
        return regions, zones

    # --------------------------------------------------------------------
    def get_gcp_zones(self, region, zones):
        """Get GCP Zones for a region for zones already received from region call"""
        region_zones = []
        for zone in zones:
            if region in zone:
                region_zones.append(zone)
        return region_zones

    # --------------------------------------------------------------------
    def get_gcp_images(self, sles_or_sap, os):
        """Get GCP Images"""
        """GCP has PROJECT and FAMILY"""
        """PROJECT suse-cloud is for SLES with FAMILY, sles-12 and sles15"""
        """PROJECT suse-sap-cloud is for SLE-SAP with FAMILY, sles-12-sp2-sap, sles-12-sp3-sap, sles-12-sp4-sap, sles-12-sp5-sap, sles-15-sap, sles-15-sp1-sap"""
        """can use list with project suse-cloud and filter name=sles-12-sp5*"""

        # TODO: need to improve so no versions are hardcoded
        if os == "sles-15":
            sys.exit("No GCP images for this OS. Exiting")
        credentials = GoogleCredentials.get_application_default()
        service = discovery.build(
            'compute', 'v1', credentials=credentials)
        gcp_images = []
        if sles_or_sap == "sles":
            project = "suse-cloud"
        elif sles_or_sap == "sles-sap":
            project = "suse-sap-cloud"
            # In GCP, SUSE SAP images are named sles-12-spX-sap instead of
            # the expected sles-sap-12-spX so change this to get
            # images
            temp_os = os.split("-")
            if (os == "sles-sap-15"):
                os = temp_os[0] + '-' + temp_os[2] + \
                    '-' + temp_os[1]
            else:
                os = temp_os[0] + '-' + temp_os[2] + \
                    '-' + temp_os[3] + '-' + temp_os[1]

        filter = "name=" + os + "*"
        request = service.images().list(project=project, filter=filter)
        # response is dict, what if no 'items' key, then no images
        response = request.execute()
        if "items" in response.keys():
            for image in response['items']:
                gcp_images.append(image['name'])
            request = service.images().list_next(
                previous_request=request, previous_response=response)
            return gcp_images
