import pulumi
from pulumi_azure_native.resources import ResourceGroup

from azure_infra import bastion, common, names, network

# from bastion_app import bastion_management


def main():

    location = "eastus"
    tags = {
        "env": "dev",
        "agg": "common",
    }
    # Create resource group
    rg = ResourceGroup(
        names.RG_COMMON_NAME,
        location=location,
        tags=tags,
        resource_group_name=names.RG_COMMON_NAME,
        # opts=pulumi.ResourceOptions(import_=names.RG_COMMON_NAME),
    )
    pulumi.export(names.EXPORT_RG_COMMON_ID, rg.id)

    # Create networks
    networks = network.apply(rg, tags)

    # Create bastion
    rg_bastion = ResourceGroup(
        names.RG_BASTION_NAME,
        location=location,
        tags=tags,
        resource_group_name=names.RG_BASTION_NAME,
    )
    pulumi.export(names.EXPORT_RG_BASTION_ID, rg.id)
    bastion_host = bastion.apply(rg_bastion, networks["bastion"], tags)
    common_resources = common.apply(rg, networks["bastion"], tags)
