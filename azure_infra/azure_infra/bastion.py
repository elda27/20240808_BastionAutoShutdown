import pulumi
from pulumi_azure_native.network import (
    BastionHost,
    BastionHostSkuName,
    PublicIPAddress,
    Subnet,
)
from pulumi_azure_native.resources import ResourceGroup

from azure_infra import names


def apply(rg: ResourceGroup, subnet: Subnet, tags: dict[str, str]) -> BastionHost:
    ip = PublicIPAddress(
        names.BASTION_IP_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        public_ip_allocation_method="Static",
        public_ip_address_version="IPv4",
        tags=tags,
        public_ip_address_name=names.BASTION_IP_NAME,
    )
    bastion = BastionHost(
        names.BASTION_RESOURCE_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        ip_configurations=[
            {
                "name": "bastion-ip-conf",
                "public_ip_address": {"id": ip.id},
                "subnet": {"id": subnet.id},
            }
        ],
        sku={"name": BastionHostSkuName.STANDARD},
        tags=tags,
        bastion_host_name=names.BASTION_RESOURCE_NAME,
    )

    pulumi.export(names.EXPORT_BASTION_RESOURCE_ID, bastion.id)
    pulumi.export(names.EXPORT_BASTION_IP_ID, ip.id)

    return bastion
