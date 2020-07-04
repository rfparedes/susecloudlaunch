from constants import *
from azure.common.client_factory import get_client_from_cli_profile
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.compute import ComputeManagementClient


class AzureInstance:

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

    def get_azure_regions_azs(self):
        subscription_client = get_client_from_cli_profile(
            SubscriptionClient)
        subscription = next(subscription_client.subscriptions.list())
        locations = subscription_client.subscriptions.list_locations(
            subscription.subscription_id)
        regions = []
        for location in locations:
            regions.append(location.name)
        return sorted(regions)

    def get_azure_images(self, region):

        publisher = "SUSE"
        compute_client = get_client_from_cli_profile(
            ComputeManagementClient)

        result_list_offers = compute_client.virtual_machine_images.list_offers(region, publisher,
                                                                               )
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

                    print('PUBLISHER: {0}, OFFER: {1}, SKU: {2}, VERSION: {3}'.format(
                        publisher,
                        offer.name,
                        sku.name,
                        version.name,
                    ))
