from typing import TypedDict

from pulumi_azure_native.network import NetworkSecurityGroup, Subnet, VirtualNetwork
from pulumi_azure_native.resources import ResourceGroup

from azure_infra import names


class DefinedNetworks(TypedDict):
    root: VirtualNetwork
    bastion: Subnet
    common_vm: Subnet


class DefinedNsgs(TypedDict):
    bastion: NetworkSecurityGroup
    common_vm: NetworkSecurityGroup


def apply(rg: ResourceGroup) -> DefinedNetworks:
    root = VirtualNetwork(
        names.VNET_COMMON_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        address_space={"address_prefix": "10.0.0.0/16"},
    )

    nsgs = apply_nsgs(rg)

    subnet_vm = Subnet(
        names.SUBNET_COMMON_VM_NAME,
        resource_group_name=rg.name,
        address_prefix="10.0.1.0/28",
        network_security_group=nsgs["common_vm"],
        virtual_network_name=root.name,
    )
    subnet_bastion = Subnet(
        names.SUBNET_BASTION_NAME,
        resource_group_name=rg.name,
        address_prefix="10.0.2.0/25",
        network_security_group=nsgs["bastion"],
        virtual_network_name=root.name,
    )

    return {
        "root": root,
        "bastion": subnet_bastion,
        "common_vm": subnet_vm,
    }


def apply_nsgs(rg: ResourceGroup) -> DefinedNsgs:
    nsg_bastion = NetworkSecurityGroup(
        names.NSG_BASTION_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        security_rules=[
            # Inbound
            {
                "name": "Allow RDP",
                "priority": 1000,
                "access": "Allow",
                "direction": "Inbound",
                "destination_port_range": "3389",
                "protocol": "Tcp",
                "source_port_range": "*",
                "source_address_prefix": "*",
                "destination_address_prefix": "*",
            },
            {
                "name": "Allow https",
                "priority": 1100,
                "access": "Allow",
                "direction": "Inbound",
                "destination_port_range": "443",
                "protocol": "Tcp",
                "source_port_range": "*",
                "source_address_prefix": "*",
                "destination_address_prefix": "*",
            },
            {
                "name": "Deny http",
                "protocol": "Tcp",
                "access": "Deny",
                "direction": "Inbound",
                "destination_port_range": "80",
                "source_port_range": "*",
                "source_address_prefix": "*",
                "destination_address_prefix": "*",
                "priority": 1200,
            },
            # Outbound
            {
                "name": "Allow between VNets",
                "protocol": "*",
                "source_address_prefix": "VirtualNetwork",
                "destination_address_prefix": "VirtualNetwork",
                "access": "Allow",
                "direction": "Outbound",
                "source_port_range": "*",
                "destination_port_range": "*",
                "priority": 100,
            },
            {
                "name": "Deny all",
                "protocol": "*",
                "source_address_prefix": "*",
                "destination_address_prefix": "*",
                "access": "Deny",
                "direction": "Outbound",
                "source_port_range": "*",
                "destination_port_range": "*",
                "priority": 4096,
            },
        ],
    )

    nsg_common_vm = NetworkSecurityGroup(
        names.NSG_COMMON_VM_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        security_rules=[
            {
                "name": "Allow between VNets",
                "protocol": "*",
                "source_address_prefix": "VirtualNetwork",
                "destination_address_prefix": "VirtualNetwork",
                "access": "Allow",
                "direction": "Inbound",
                "source_port_range": "*",
                "destination_port_range": "*",
                "priority": 100,
            },
            {
                "name": "Deny all",
                "protocol": "*",
                "source_address_prefix": "*",
                "destination_address_prefix": "*",
                "access": "Deny",
                "direction": "Inbound",
                "source_port_range": "*",
                "destination_port_range": "*",
                "priority": 4096,
            },
            # Outbound
            {
                "name": "Allow between VNets",
                "protocol": "*",
                "source_address_prefix": "VirtualNetwork",
                "destination_address_prefix": "VirtualNetwork",
                "access": "Allow",
                "direction": "Outbound",
                "source_port_range": "*",
                "destination_port_range": "*",
                "priority": 100,
            },
            {
                "name": "Deny all",
                "protocol": "*",
                "source_address_prefix": "*",
                "destination_address_prefix": "*",
                "access": "Deny",
                "direction": "Outbound",
                "source_port_range": "*",
                "destination_port_range": "*",
                "priority": 4096,
            },
        ],
    )

    return {
        "bastion": nsg_bastion,
        "common_vm": nsg_common_vm,
    }
