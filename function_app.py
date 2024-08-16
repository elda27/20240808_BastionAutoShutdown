import json
import os
from datetime import datetime
from logging import getLogger
from typing import TypedDict

import azure.cosmos as cosmos
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
credential = DefaultAzureCredential()

client = CosmosClient(TARGET_COSMOSDB_ACCOUNT, credential)
database = client.get_database_client(TARGET_COSMOSDB_DATABASE)
container = database.get_container_client(TARGET_COSMOSDB_CONTAINER)


class Record(TypedDict):
    id: str
    Title: str
    Start: str
    End: str


@app.route(route="handle")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logger.info("Python HTTP trigger function processed a request.")
    logger.info(f"TARGET_SUBSCRIPTION_ID: {TARGET_SUBSCRIPTION_ID}")
    logger.info(f"TARGET_RESOURCE_GROUP: {TARGET_RESOURCE_GROUP}")
    logger.info(f"TARGET_RESOURCE_NAME: {TARGET_RESOURCE_NAME}")
    logger.info(f"TARGET_RESOURCE_ARM_TEMPLATE: {TARGET_RESOURCE_ARM_TEMPLATE}")

    records = read_data_from_cosmos()
    now = datetime.now()
    flag_create_resource = False
    # Check if the resource should be created
    for record in records:
        if datetime.fromisoformat(record["Start"]) >= now:
            flag_create_resource = True
        if datetime.fromisoformat(record["End"]) >= now:
            container.delete_item(record["id"], record["Title"])

    if flag_create_resource:
        # Create resource if not available
        if has_target_resource():
            message = "Resource already exists"
        else:
            message = "Resource does not exist"
            create_resource()
    else:
        message = "Resource not created"

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


def create_resource():
    """Create resources using azure api"""
    resource_client = ResourceManagementClient(credential, TARGET_SUBSCRIPTION_ID)
    resource_client.resources.create_or_update(
        TARGET_RESOURCE_GROUP, TARGET_RESOURCE_NAME, TARGET_RESOURCE_ARM_TEMPLATE
    )


def has_target_resource() -> bool:
    """Read resources using azure api"""
    resource_client = ResourceManagementClient(credential, TARGET_SUBSCRIPTION_ID)
    resources = resource_client.resource_groups.list_resources(TARGET_RESOURCE_GROUP)
    for resource in resources:
        if resource.name is not None and resource.name == TARGET_RESOURCE_NAME:
            return True
    return False
