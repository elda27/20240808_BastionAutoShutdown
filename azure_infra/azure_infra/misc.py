import pulumi_azure_native as azure_native
from pulumi_azure_native.documentdb import DatabaseAccount
from pulumi_azure_native.resources import ResourceGroup
from pulumi_azure_native.storage import StorageAccount

import pulumi


def get_storage_primary_key(
    rg: ResourceGroup, storage: StorageAccount
) -> pulumi.Output[str]:
    """Get the primary access key for a storage account.

    Parameters
    ----------
    rg : ResourceGroup
        resource group of the storage
    storage : StorageAccount
        Storage account

    Returns
    -------
    pulumi.Output[str]
        Access key string for the storage account
    """
    return (
        pulumi.Output.all(rg.name, storage.name)
        .apply(
            lambda args: azure_native.storage.list_storage_account_keys(
                args[1],
                resource_group_name=args[0],
            )
        )
        .apply(lambda x: pulumi.Output.secret(x.keys[0].value))
    )


def get_storage_connection_string(
    rg: ResourceGroup,
    storage: azure_native.storage.StorageAccount,
) -> pulumi.Output[str]:
    """Get a connection string for a storage account.

    Parameters
    ----------
    rg : ResourceGroup
        resource group of the storage
    storage : StorageAccount
        Storage account

    Returns
    -------
    pulumi.Output[str]
        Connection string for the storage account
    """
    return pulumi.Output.all(storage.name, get_storage_primary_key(rg, storage)).apply(
        lambda args: pulumi.Output.secret(
            f"DefaultEndpointsProtocol=https;AccountName={args[0]};AccountKey={args[1]}"
        )
    )


def get_documentdb_primary_key(
    rg: ResourceGroup, cosmosdb: DatabaseAccount
) -> pulumi.Output[str]:
    """Get the primary access key for a CosmosDB account.

    Parameters
    ----------
    rg : ResourceGroup
        resource group of the cosmosdb
    cosmosdb : DatabaseAccount
        Database account

    Returns
    -------
    pulumi.Output[str]
        Connection string for the cosmosdb
    """
    return (
        pulumi.Output.all(cosmosdb.name, rg.name, cosmosdb)
        .apply(
            lambda args: azure_native.documentdb.list_database_account_keys(
                args[0],
                resource_group_name=args[1],
            )
        )
        .apply(lambda x: pulumi.Output.secret(x.primary_master_key))
    )


def get_documentdb_connection_string(
    rg: ResourceGroup, cosmosdb: DatabaseAccount
) -> pulumi.Output[str]:
    """Get the connection string for a CosmosDB account.

    Parameters
    ----------
    rg : ResourceGroup
        resource group of the cosmosdb
    cosmosdb : DatabaseAccount
        Database account

    Returns
    -------
    pulumi.Output[str]
        Connection string for the cosmosdb
    """
    return pulumi.Output.all(
        cosmosdb.name, get_documentdb_primary_key(rg, cosmosdb)
    ).apply(
        lambda args: pulumi.Output.secret(
            f"AccountEndpoint=https://{args[0]}.documents.azure.com:443/;AccountKey={args[1]};"
        )
    )
