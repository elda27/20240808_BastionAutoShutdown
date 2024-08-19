import json
from pathlib import Path
from typing import Literal, TypedDict

import azure_infra.names as common_names
import jinja2
import pulumi
import pulumi_azure_native as azure_native
from pulumi_azure_native.app import LogicApp
from pulumi_azure_native.documentdb import DatabaseAccount
from pulumi_azure_native.logic import Workflow
from pulumi_azure_native.resources import ResourceGroup
from pulumi_azure_native.storage import StorageAccount
from pulumi_azure_native.web import AppServicePlan, AzureStorageType, WebApp

from bastion_management import names

current_dir = Path(__file__).parent


class DefinedResources(TypedDict):
    register_logic_app: LogicApp
    # handle_logic_app: LogicApp
    handler_app: WebApp


def apply_bastion_management(
    rg: ResourceGroup,
    tags: dict[str, str],
    stack: pulumi.StackReference,
) -> DefinedResources:
    """Apply bastion management resources.

    Parameters
    ----------
    rg : ResourceGroup
        Resource group for bastion management resources.
    tags : dict[str, str]
        tags for resources
    shared_file : StorageAccount
        Shared file for azure function.
    pulumi_storage : StorageAccount
        Storage account for pulumi state.
    cosmosdb : DatabaseAccount
        CosmosDB account for state management.

    Returns
    -------
    DefinedResources
        _description_
    """
    config = pulumi.Config()

    # logicapp_definitions = read_logicapp_template(rg, "register")
    # register_logic_app = LogicApp(
    #     names.BM_LOGIC_REGISTER_NAME,
    #     logic_app_name=names.BM_LOGIC_REGISTER_NAME,
    #     resource_group_name=rg.name,
    # )
    register_logic_app = Workflow(
        names.BM_LOGIC_REGISTER_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        definition=read_logicapp_template(rg, "register"),
        workflow_name=names.BM_LOGIC_REGISTER_NAME,
    )

    handler_service_plan = AppServicePlan(
        names.BM_APPSERVICE_PLAN_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        tags=tags,
        # see: https://learn.microsoft.com/ja-jp/azure/virtual-network/ip-services/configure-public-ip-bastion
        # az rest --method get --url https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Web/serverfarms?api-version=2023-12-01
        sku={
            "name": "Y1",
            "tier": "Dynamic",
            "size": "Y1",
            "family": "Y",
            "capacity": 0,
        },
    )

    # CosmosDB
    file_access_key = stack.get_output(
        common_names.EXPORT_COMMON_SYSAD_FILE_PRIMARY_KEY
    )
    blob_connection_string = stack.get_output(
        common_names.EXPORT_COMMON_SYSAD_STORAGE_CONNECTION_STRING
    )
    cosmosdb_connection_string = stack.get_output(
        common_names.EXPORT_COMMON_SYSAD_COSMOSDB_CONNECTION_STRING
    )

    # Create function app
    envs = {
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "AzureWebJobsFeatureFlags": "EnableWorkerIndexing",
        "TARGET_ARNS": "",
        "PULUMI_BACKEND_URL": f"https://{common_names.COMMON_SYSAD_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/iac/pulumi/",
        "PULUMI_SKIP_CONFIRMATIONS": "true",
        "PULUMI_CONFIG_PASSPHRASE": config.require_secret("PULUMI_PASSWORD"),
        "AZURE_STORAGE_CONNECTION_STRING": blob_connection_string,  # For pulumi
        "NO_COLOR": "true",
    }
    handler_app = WebApp(
        names.BM_FUNC_HANDLER_NAME,
        resource_group_name=rg.name,
        location=rg.location,
        tags=tags,
        server_farm_id=handler_service_plan.id,
        site_config={
            "app_settings": [{"name": key, "value": val} for key, val in envs.items()],
            "http20_enabled": True,
            "connection_strings": [
                {
                    "name": "DOCUMENTDB",
                    "connection_string": cosmosdb_connection_string,
                    "type": azure_native.web.ConnectionStringType.DOC_DB,
                }
            ],
            "azure_storage_accounts": {
                "pulumi-root": {
                    "type": AzureStorageType.AZURE_FILES,
                    "name": "AzureWebJobsStorage",
                    "account_name": common_names.COMMON_SYSAD_FILE_ACCOUNT_NAME,
                    "share_name": "iac",
                    "access_key": file_access_key,
                    "mount_path": "/mnt/pulumi",
                }
            },
        },
        https_only=True,
    )

    return {
        "register_logic_app": register_logic_app,
        "handler_app": handler_app,
    }


apply = apply_bastion_management


def read_logicapp_template(
    rg: ResourceGroup,
    name: str,
    key: Literal["definition", "properties", None] = "definition",
) -> dict:
    template_path = current_dir / "templates" / f"{name}.json.j2"
    subscription_id = rg.id.apply(lambda rg_id: rg_id.split("/")[2])
    result = (
        pulumi.Output.all(rg.name, rg.location, subscription_id)
        .apply(
            lambda args: jinja2.Template(template_path.read_text()).render(
                resource_group_name=args[0],
                location=args[1],
                subscription_id=args[2],
            )
        )
        .apply(
            lambda content: (
                json.loads(content)[key] if key is not None else json.loads(content)
            )
        )
    )
    return result
