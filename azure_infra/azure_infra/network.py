from typing import TypedDict

import pulumi
from pulumi_azure_native import network
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


def apply(rg: ResourceGroup, tags: dict[str, str]) -> DefinedNetworks:
    root = VirtualNetwork(
        names.VNET_COMMON_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        address_space={"address_prefixes": ["10.0.0.0/16"]},
        tags=tags,
    )

    nsgs = apply_nsgs(rg)

    subnet_vm = Subnet(
        names.SUBNET_COMMON_VM_NAME,
        resource_group_name=rg.name,
        address_prefix="10.0.1.0/28",
        network_security_group={"id": nsgs["common_vm"].id},
        virtual_network_name=root.name,
    )
    subnet_bastion = Subnet(
        names.SUBNET_BASTION_NAME,
        resource_group_name=rg.name,
        address_prefix="10.0.2.0/25",
        network_security_group={"id": nsgs["bastion"].id},
        virtual_network_name=root.name,
    )

    # Export the subnet ids
    pulumi.export(names.EXPORT_SUBNET_COMMON_VM_ID, subnet_vm.id)
    pulumi.export(names.EXPORT_SUBNET_BASTION_ID, subnet_bastion.id)
    pulumi.export(names.EXPORT_VNET_COMMON_ID, root.id)

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
        # See: https://learn.microsoft.com/ja-jp/azure/bastion/bastion-nsg
        security_rules=[
            # Inbound
            network.SecurityRuleArgs(
                name="AllowHTTPInbound",
                priority=100,
                protocol="Tcp",
                direction="Inbound",
                access="Allow",
                source_port_range="*",
                destination_port_range="443",
                source_address_prefix="Internet",
                destination_address_prefix="*",
            ),
            network.SecurityRuleArgs(
                name="AllowGatewayInbound",
                priority=110,
                protocol="Tcp",
                direction="Inbound",
                access="Allow",
                source_port_range="*",
                destination_port_range="443",
                source_address_prefix="GatewayManager",
                destination_address_prefix="*",
            ),
            network.SecurityRuleArgs(
                name="AllowPublicInbound",
                priority=120,
                protocol="Tcp",
                direction="Inbound",
                access="Allow",
                source_port_range="*",
                destination_port_range="443",
                source_address_prefix="AzureLoadBalancer",
                destination_address_prefix="*",
            ),
            network.SecurityRuleArgs(
                name="AllowBastionHostCommunication",
                priority=130,
                protocol="*",
                direction="Inbound",
                access="Allow",
                source_port_ranges=["8080", "5701"],
                destination_port_ranges=["8080", "5701"],
                source_address_prefix="VirtualNetwork",
                destination_address_prefix="VirtualNetwork",
            ),
            # Outbound
            network.SecurityRuleArgs(
                name="AllowSshRdpOutbound",
                priority=100,
                protocol="*",
                direction="Outbound",
                access="Allow",
                source_port_range="*",
                destination_port_ranges=["22", "3389"],
                source_address_prefix="*",
                destination_address_prefix="VirtualNetwork",
            ),
            network.SecurityRuleArgs(
                name="AllowAzureCloudOutbound",
                priority=110,
                protocol="Tcp",
                direction="Outbound",
                access="Allow",
                source_port_range="*",
                destination_port_range="443",
                source_address_prefix="*",
                destination_address_prefix="AzureCloud",
            ),
            network.SecurityRuleArgs(
                name="AllowBastionCommunication",
                priority=120,
                protocol="*",
                direction="Outbound",
                access="Allow",
                source_port_ranges=["8080", "5701"],
                destination_port_ranges=["8080", "5701"],
                source_address_prefix="VirtualNetwork",
                destination_address_prefix="VirtualNetwork",
            ),
            network.SecurityRuleArgs(
                name="AllowHttpOutbound",
                priority=130,
                protocol="*",
                direction="Outbound",
                access="Allow",
                source_port_range="*",
                destination_port_range="80",
                source_address_prefix="*",
                destination_address_prefix="Internet",
            ),
        ],
    )

    nsg_common_vm = NetworkSecurityGroup(
        names.NSG_COMMON_VM_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        security_rules=[
            # Inbound
            {
                "name": "allow-between-vnets-inbound",
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
                "name": "deny-all-inbound",
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
                "name": "allow-between-vnets-outbound",
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
                "name": "deny-all-outbound",
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

    pulumi.export(names.EXPORT_NSG_BASTION_ID, nsg_bastion.id)
    pulumi.export(names.EXPORT_NSG_COMMON_VM_ID, nsg_common_vm.id)

    return {
        "bastion": nsg_bastion,
        "common_vm": nsg_common_vm,
    }
