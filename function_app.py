import json
import os
import subprocess
from contextlib import contextmanager
from datetime import datetime
from logging import getLogger
from pathlib import Path
from typing import TypedDict

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

logger = getLogger(__name__)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
TARGET_SUBSCRIPTION_ID = os.getenv("TARGET_SUBSCRIPTION_ID", "")
TARGET_RESOURCE_GROUP = os.getenv("TARGET_RESOURCE_GROUP", "")
TARGET_RESOURCE_NAME = os.getenv("TARGET_RESOURCE_NAME", "")
TARGET_RESOURCE_ARM_TEMPLATE = os.getenv("TARGET_RESOURCE_ARM_TEMPLATE", "")
TARGET_COSMOSDB_ACCOUNT = os.getenv("TARGET_COSMOSDB_ACCOUNT", "")
TARGET_COSMOSDB_DATABASE = os.getenv("TARGET_COSMOSDB_DATABASE", "BastionManagement")
TARGET_COSMOSDB_CONTAINER = os.getenv("TARGET_COSMOSDB_CONTAINER", "Entries")
TARGET_ARNS = os.getenv("TARGET_ARNS", "").split(";")

credential = DefaultAzureCredential()

client = CosmosClient(TARGET_COSMOSDB_ACCOUNT, credential)
database = client.get_database_client(TARGET_COSMOSDB_DATABASE)
container = database.get_container_client(TARGET_COSMOSDB_CONTAINER)

CURRENT_DIR = Path(__file__).parent
PULUMI_DIR = CURRENT_DIR / "pulumi"


@contextmanager
def context_path(paths: list[str]):
    """Context manager for changing the current working directory."""
    try:
        path = os.environ.get("PATH", "")
        if os.name == "nt":
            pathsep = ";"
        else:
            pathsep = ":"
        os.environ["PATH"] = pathsep.join([path] + paths)
    finally:
        os.environ["PATH"] = path


class Record(TypedDict):
    id: str
    title: str
    start: str
    end: str


@app.cosmos_db_trigger(
    arg_name="azcosmosdb",
    container_name="BastionManagement",
    database_name="Entries",
    connection="DOCUMENTDB",
)
def http_trigger(azcosmosdb: func.DocumentList) -> func.HttpResponse:
    logger.info("Python HTTP trigger function processed a request.")
    logger.info(f"TARGET_SUBSCRIPTION_ID: {TARGET_SUBSCRIPTION_ID}")
    logger.info(f"TARGET_RESOURCE_GROUP: {TARGET_RESOURCE_GROUP}")
    logger.info(f"TARGET_RESOURCE_NAME: {TARGET_RESOURCE_NAME}")
    logger.info(f"TARGET_RESOURCE_ARM_TEMPLATE: {TARGET_RESOURCE_ARM_TEMPLATE}")
    records = azcosmosdb.data
    # records = read_data_from_cosmos()
    now = datetime.now()
    flag_create_resource = False
    flag_delete_resource = False
    # Check if the resource should be created
    for record in records:
        if datetime.fromisoformat(record["start"]) >= now:
            flag_create_resource = True
        if datetime.fromisoformat(record["end"]) >= now:
            container.delete_item(record["id"], record["title"])
            flag_delete_resource = True

    if flag_create_resource:
        # Create resource if not available
        if has_target_resource():
            message = "Resource already exists"
        else:
            message = "Resource does not exist"
            create_resources()
    elif flag_delete_resource:
        message = "Resource deleted"
        delete_resources()
    else:
        message = "No action required"

    logger.info(f"Execution: {message}")
    return func.HttpResponse(
        json.dumps(
            {
                "status": "success",
                "message": message,
                "num_records": len(records),
            }
        ),
        status_code=200,
    )


def read_data_from_cosmos() -> list[Record]:
    """Read data from cosmos db"""
    items = container.query_items(
        query="SELECT * FROM c", enable_cross_partition_query=True
    )
    return items  # type: ignore


def format_arns(arns: list[str]) -> str:
    """Format arns"""
    return " ".join([f"--target {arn}" for arn in arns])


def create_resources():
    """Create resources using azure api"""
    target_arn_opts = format_arns(TARGET_ARNS)
    with context_path("/mnt/pulumi"):
        subprocess.check_call("pulumi login", cwd=str(PULUMI_DIR), shell=True)
        subprocess.check_call(
            f"pulumi up -y {target_arn_opts}", cwd=str(PULUMI_DIR), shell=True
        )


def delete_resources():
    """Delete resources using azure api"""
    target_arn_opts = format_arns(TARGET_ARNS)
    with context_path("/mnt/pulumi"):
        subprocess.check_call("pulumi login", cwd=str(PULUMI_DIR), shell=True)
        subprocess.check_call(
            f"pulumi destroy -y {target_arn_opts}", cwd=str(PULUMI_DIR), shell=True
        )


def has_target_resource() -> bool:
    """Read resources using azure api"""
    resource_client = ResourceManagementClient(credential, TARGET_SUBSCRIPTION_ID)
    resources = resource_client.resource_groups.list_resources(TARGET_RESOURCE_GROUP)
    for resource in resources:
        if resource.name is not None and resource.name == TARGET_RESOURCE_NAME:
            return True
    return False
