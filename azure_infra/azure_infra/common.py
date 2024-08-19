from typing import TypedDict

import pulumi
import pulumi_azure_native as azure_native
from pulumi_azure_native.compute import VirtualMachine
from pulumi_azure_native.documentdb import DatabaseAccount
from pulumi_azure_native.network import NetworkInterface, Subnet
from pulumi_azure_native.resources import ResourceGroup
from pulumi_azure_native.storage import StorageAccount

from azure_infra import misc, names


class DefinedResources(TypedDict):
    vm001: VirtualMachine
    nic001: NetworkInterface
    storage_sysad001: StorageAccount
    file_sysad001: StorageAccount
    cosmosdb: DatabaseAccount


def apply(rg: ResourceGroup, subnet: Subnet, tags: dict[str, str]) -> DefinedResources:
    # Azure storage v2
    storage001 = StorageAccount(
        names.COMMON_SYSAD_STORAGE_ACCOUNT_NAME,
        resource_group_name=rg.name,
        kind=azure_native.storage.Kind.STORAGE_V2,
        sku={"name": azure_native.storage.SkuName.STANDARD_LRS},
        access_tier=azure_native.storage.AccessTier.HOT,
        enable_https_traffic_only=True,
        public_network_access=azure_native.storage.PublicNetworkAccess.ENABLED,
        location=rg.location,
        tags=tags,
        # account_name=names.IMPORTED_COMMON_SYSAD_STORAGE_ACCOUNT_NAME,
        # opts=pulumi.ResourceOptions(
        #     import_=names.IMPORTED_COMMON_SYSAD_STORAGE_ACCOUNT_NAME
        # ),
    )
    # Azure file storage
    file001 = StorageAccount(
        names.COMMON_SYSAD_FILE_ACCOUNT_NAME,
        resource_group_name=rg.name,
        kind=azure_native.storage.Kind.FILE_STORAGE,
        sku={"name": azure_native.storage.SkuName.PREMIUM_LRS},
        access_tier=azure_native.storage.AccessTier.HOT,
        enable_https_traffic_only=True,
        public_network_access=azure_native.storage.PublicNetworkAccess.ENABLED,
        location=rg.location,
        tags=tags,
    )

    # Cosmos DB
    cosmosdb = DatabaseAccount(
        names.COMMON_SYSAD_COSMOSDB_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        locations=[{"location_name": rg.location, "failover_priority": 0}],
        kind=azure_native.documentdb.DatabaseAccountKind.GLOBAL_DOCUMENT_DB,
        database_account_offer_type=azure_native.documentdb.DatabaseAccountOfferType.STANDARD,
        tags=tags,
    )

    # Network interface for vm001
    nic = NetworkInterface(
        names.NIC_COMMON_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        ip_configurations=[
            {
                "name": "inet1",
                "subnet": {"id": subnet.id},
            }
        ],
        tags=tags,
    )

    # SSH public key
    # azure_native.compute.SshPublicKey(

    # )

    # Virtual machine
    vm = VirtualMachine(
        names.VM_COMMON_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        hardware_profile={"vm_size": "Standard_DS1_v2"},
        network_profile={"network_interfaces": [{"id": nic.id}]},
        os_profile={
            "computer_name": names.VM_COMMON_NAME,
            "admin_username": "adminuser",
            "admin_password": "Password1234wjijznu21iijsaads221",
        },
        storage_profile={
            # See: az vm image list --output table
            # https://learn.microsoft.com/en-us/azure/virtual-machines/linux/cli-ps-findimage
            "image_reference": {
                "publisher": "Canonical",
                "offer": "0001-com-ubuntu-server-jammy",
                "sku": "22_04-lts",
                "version": "latest",
            },
            "os_disk": {
                "caching": azure_native.compute.CachingTypes.READ_WRITE,
                "create_option": azure_native.compute.DiskCreateOptionTypes.FROM_IMAGE,
                "managed_disk": {
                    "storage_account_type": azure_native.compute.StorageAccountTypes.PREMIUM_LRS,
                },
                "name": names.VM_COMMON_DISK_NAME,
            },
        },
        tags=tags,
    )

    # Export ids
    pulumi.export(names.EXPORT_VM_COMMON_ID, vm.id)
    pulumi.export(names.EXPORT_NIC_COMMON_ID, nic.id)
    pulumi.export(names.EXPORT_STORAGE_SYSAD_ID, storage001.id)
    pulumi.export(names.EXPORT_FILE_SYSAD_ID, file001.id)
    pulumi.export(names.EXPORT_COSMOSDB_SYSAD_ID, cosmosdb.id)

    # Export secret keys
    pulumi.export(
        names.EXPORT_COMMON_SYSAD_STORAGE_PRIMARY_KEY,
        misc.get_storage_primary_key(rg, storage001),
    )
    pulumi.export(
        names.EXPORT_COMMON_SYSAD_STORAGE_CONNECTION_STRING,
        misc.get_storage_connection_string(rg, storage001),
    )
    pulumi.export(
        names.EXPORT_COMMON_SYSAD_FILE_PRIMARY_KEY,
        misc.get_storage_primary_key(rg, file001),
    )
    pulumi.export(
        names.EXPORT_COMMON_SYSAD_FILE_CONNECTION_STRING,
        misc.get_storage_connection_string(rg, file001),
    )
    pulumi.export(
        names.EXPORT_COMMON_SYSAD_COSMOSDB_PRIMARY_KEY,
        misc.get_documentdb_primary_key(rg, cosmosdb),
    )
    pulumi.export(
        names.EXPORT_COMMON_SYSAD_COSMOSDB_CONNECTION_STRING,
        misc.get_documentdb_connection_string(rg, cosmosdb),
    )

    return {
        "vm001": vm,
        "nic001": nic,
        "storage_sysad001": storage001,
        "file_sysad001": file001,
        "cosmosdb": cosmosdb,
    }
