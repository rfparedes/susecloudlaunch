from constants import *
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from allproviderutil import *
import allproviderutil
import threading
import pickle


class AzureInstance:
    """Store Azure instance information"""

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

    def get_azure_regions_azs(self):
        """Get regions via Azure SDK"""
        if (not (os.path.isfile(REGION_CACHE_FILENAME + self.get_provider()))):
            subscription_client = get_client_from_cli_profile(
                SubscriptionClient)
            subscription = next(
                subscription_client.subscriptions.list())
            locations = subscription_client.subscriptions.list_locations(
                subscription.subscription_id)
            regions = []
            for location in locations:
                regions.append(location.name)
            # Cache region data
            cache_write_data(
                REGION_CACHE_FILENAME +
                self.get_provider(), regions)
        else:
            regions = cache_read_data(
                REGION_CACHE_FILENAME +
                self.get_provider())
        return sorted(regions)

    # --------------------------------------------------------------------
    def get_all_azure_images(self):
        """Get all images via Azure SDK"""
        """Azure marketplace offer names and skus are nonsensical so it's difficult to programatically determine"""
        allproviderutil.done = False
        # If no azureimagecache, go out and get images from Azure
        # TODO: if file is older than 7 days, also go out and get
        # images from Azure
        if (not (os.path.isfile('.azureimagecache'))):
            publisher = "SUSE"
            region = self.get_region()
            compute_client = get_client_from_cli_profile(
                ComputeManagementClient)
            list_of_images = []
            spin_thread = threading.Thread(target=spin_cursor)
            print(OKGREEN + "Getting Azure Images", end=" ")
            spin_thread.start()

            result_list_offers = compute_client.virtual_machine_images.list_offers(
                region, publisher,)
            for offer in result_list_offers:
                result_list_skus = compute_client.virtual_machine_images.list_skus(
                    region,
                    publisher,
                    offer.name,
                )
                for sku in result_list_skus:
                    result_list = compute_client.virtual_machine_images.list(
                        region,
                        publisher,
                        offer.name,
                        sku.name,
                    )
                    for version in result_list:
                        result_get = compute_client.virtual_machine_images.get(
                            region,
                            publisher,
                            offer.name,
                            sku.name,
                            version.name,
                        )
                        urn = (
                            publisher + ":" +
                            offer.name + ":" +
                            sku.name + ":" +
                            version.name)
                        list_of_images.append(urn)
            allproviderutil.done = True
            spin_thread.join()
            # cache the results
            allproviderutil.cache_write_data(
                ".azureimagecache", list_of_images)
            return(list_of_images)
        else:
            list_of_images = allproviderutil.cache_read_data(
                ".azureimagecache")
            return list_of_images

    # --------------------------------------------------------------------
    def get_azure_images(self, list_of_images, os, sles_or_sap):
        """Get images for specific os"""
        """This code is crap and not general enough because of the inconsistency of our marketplace offer/skus"""
        os_images = []

        new_list_of_images = self.sort_images_sles_or_sap(
            list_of_images, sles_or_sap)

        for image in new_list_of_images:
            image = image.lower()
            publisher, offer, sku, version = image.split(":")

            # images are sles-12-sp4
            if (os in 'sles-12-sp4') and ((sku in os and offer ==
                                           "sles-byos") or (sku == "12-sp4-gen2" and offer == "sles")):
                os_images.append(image)
            # images are sles-12-sp2 or sles-12-sp3
            elif (os in ['sles-12-sp2', 'sles-12-sp3']) and (sku in os and offer == "sles-byos"):
                os_images.append(image)
            # images are sles-15
            elif (os in ['sles-15'] and (sku == '15' or sku == '15-gen2') and (offer == 'sles-byos')):
                os_images.append(image)
            # images are sles-for-sap 12 sp2, sp3
            elif ('sles-sap' in offer and sku in os):
                os_images.append(image)
            # images are sles for sap 12 sp4
            elif(os in ['sles-sap-12-sp4'] and sku == '12-sp4-gen2' and offer == "sles-sap"):
                os_images.append(image)
            # images are sles for sap 15
            elif (os in ['sles-sap-15'] and (sku == '15' or sku == 'gen2-15') and (offer == 'sles-sap-byos')):
                os_images.append(image)
            # images are all others
            elif (os in offer and sku == "gen2" and os != 'sles-15'
                  and os != 'sles-sap-15'):
                os_images.append(image)

        return os_images

    def sort_images_sles_or_sap(self, list_of_images, sles_or_sap):
        """Sort images into either sles or sap"""
        sap_images = []
        sles_images = []
        for image in list_of_images:
            image = image.lower()
            publisher, offer, sku, version = image.split(":")

            if ('sles-sap' in offer):
                sap_images.append(image)
            else:
                sles_images.append(image)

        if sles_or_sap == 'sles':
            return sles_images
        else:
            return sap_images
