from typing import TypedDict

from pulumi_azure_native.compute import VirtualMachine
from pulumi_azure_native.keyvault import Vault
from pulumi_azure_native.network import NetworkInterface, Subnet
from pulumi_azure_native.resources import ResourceGroup

from azure_infra import names


class DefinedResources(TypedDict):
    vm001: VirtualMachine


def apply(rg: ResourceGroup, subnet: Subnet) -> DefinedResources:
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
    )

    vm = VirtualMachine(
        names.VM_COMMON_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        hardware_profile={"vm_size": "Standard_D2s_v5"},
        network_profile={"network_interfaces": [{"id": nic.id}]},
        os_profile={
            "computer_name": names.VM_COMMON_NAME,
            "admin_username": "adminuser",
            "admin_password": "Password1234!",
        },
    )

    return {"vm001": vm}
