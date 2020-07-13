from constants import *
from google.cloud import resource_manager
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from instance import Instance
import sys


class GCPInstance(Instance):
    """Store GCP instance information"""

    def get_gcp_projects(self):
        """Return list of projects in user account"""
        project_list = []
        client = resource_manager.Client()
        for project in client.list_projects():
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
            project = self.get_instance()
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
