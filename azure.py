from constants import *
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient
from instance import Instance
import allproviderutil
import threading
import pickle


class AzureInstance(Instance):
    """Store Azure instance information"""

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
            print('\033[1;32;40m Getting Azure Images', end=" ")
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
            f = open(".azureimagecache", "wb")
            pickle.dump(list_of_images, f)
            f.close()
            return(list_of_images)
        else:
            list_of_images = pickle.load(
                open(".azureimagecache", "rb"))
            return list_of_images

    # --------------------------------------------------------------------
    def get_azure_images(self, list_of_images, os, sles_or_sap):
        """Get images for specific os"""
        """This code is crap and not general enough because of the inconsistency of our marketplace offer/skus"""
        os_images = []

        for image in list_of_images:
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
            elif (os in offer and sku == "gen2" and os != 'sles-15' and os != 'sles-sap-15'):
                os_images.append(image)

        return os_images
