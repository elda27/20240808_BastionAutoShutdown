from azure.keyvault.secrets import KeyVaultSecret
from pulumi_azure_native.resources import ResourceGroup

from azure_infra import bastion, common, names, network


def main():
    location = "eastus"
    rg = ResourceGroup(names.RG_COMMON_NAME, location=location)
    networks = network.apply(rg)
    rg_bastion = ResourceGroup(names.RG_BASTION_NAME, location=location)
    bastion_host = bastion.apply(rg_bastion, networks["bastion"])
    common_resources = common.apply(rg, networks["bastion"])
