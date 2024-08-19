import azure_infra.names as common_names
import pulumi
from pulumi_azure_native.resources import ResourceGroup

from bastion_management import app


def main():
    # See: https://martinjt.me/2021/03/04/pulumi-multiple-projects-with-custom-backends/
    stack = pulumi.StackReference(
        "organization/bastion-auto-shutdown/dev",  # "bastion-auto-shutdown-dev"
    )
    location = "eastus"
    tags = {
        "env": "dev",
        "agg": "common",
    }
    rg_bastion = ResourceGroup.get(
        common_names.RG_BASTION_NAME,
        id=stack.get_output(common_names.EXPORT_RG_BASTION_ID),
    )

    app.apply(rg_bastion, tags, stack)
