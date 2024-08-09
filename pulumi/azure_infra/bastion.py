from pulumi_azure_native.network import BastionHost, PublicIPAddress, Subnet
from pulumi_azure_native.resources import ResourceGroup

from azure_infra import names


def apply(rg: ResourceGroup, subnet: Subnet) -> BastionHost:
    ip = PublicIPAddress(
        names.BASTION_IP_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        public_ip_allocation_method="Static",
        public_ip_address_version="IPv4",
    )
    bastion = BastionHost(
        names.BASTION_RESOURCE_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        ip_configurations=[
            {"public_ip_address": {"id": ip.id}, "subnet": {"id": subnet.id}}
        ],
        sku={"name": "Standard", "tier": "Standard"},
    )
    return bastion
