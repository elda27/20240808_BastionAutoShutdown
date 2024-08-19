# Resrouce Group Names
RG_COMMON_NAME = "rg-sysad-common-test-dev"
RG_BASTION_NAME = "rg-sysad-bastion-dev"

# Networks
VNET_COMMON_NAME = "vnet-common-dev"
SUBNET_COMMON_VM_NAME = "subnet-common_vm-dev"
SUBNET_BASTION_NAME = "AzureBastionSubnet"  # Azure Bastion requires this name

# Network Security Groups
NSG_COMMON_VM_NAME = "nsg-common_vm-dev"
NSG_BASTION_NAME = "nsg-bastion-dev"

# Bastion Names
BASTION_RESOURCE_NAME = "bastion-common-dev"
BASTION_HOST_NAME = "bastion-common-dev"
BASTION_IP_NAME = "ip-bastion-common-dev"

# Common resource names
KEYVAULT_COMMON_NAME = "kv-common-dev"
VM_COMMON_NAME = "vm001-common-dev"
VM_COMMON_DISK_NAME = "vm001-disk-common-dev"
NIC_COMMON_NAME = "nic001-common-dev"

# Common resources for system management
COMMON_SYSAD_STORAGE_ACCOUNT_NAME = "sysad001"  # Not managed by pulumi
COMMON_SYSAD_FILE_ACCOUNT_NAME = "filesysad001"
COMMON_SYSAD_COSMOSDB_NAME = "cosmos-sysad-dev"

# Export resource ids
EXPORT_VM_COMMON_ID = f"{VM_COMMON_NAME}_id"
EXPORT_NIC_COMMON_ID = f"{NIC_COMMON_NAME}_id"
EXPORT_STORAGE_SYSAD_ID = f"{COMMON_SYSAD_STORAGE_ACCOUNT_NAME}_id"
EXPORT_FILE_SYSAD_ID = f"{COMMON_SYSAD_FILE_ACCOUNT_NAME}_id"
EXPORT_COSMOSDB_SYSAD_ID = f"{COMMON_SYSAD_COSMOSDB_NAME}_id"
EXPORT_RG_COMMON_ID = f"{RG_COMMON_NAME}_id"
EXPORT_RG_BASTION_ID = f"{RG_BASTION_NAME}_id"
EXPORT_BASTION_RESOURCE_ID = f"{BASTION_RESOURCE_NAME}_id"
EXPORT_BASTION_IP_ID = f"{BASTION_IP_NAME}_id"
EXPORT_NSG_COMMON_VM_ID = f"{NSG_COMMON_VM_NAME}_id"
EXPORT_NSG_BASTION_ID = f"{NSG_BASTION_NAME}_id"
EXPORT_VNET_COMMON_ID = f"{VNET_COMMON_NAME}_id"
EXPORT_SUBNET_BASTION_ID = f"{SUBNET_BASTION_NAME}_id"
EXPORT_SUBNET_COMMON_VM_ID = f"{SUBNET_COMMON_VM_NAME}_id"

# Export resource secrets
EXPORT_COMMON_SYSAD_STORAGE_CONNECTION_STRING = (
    f"{COMMON_SYSAD_STORAGE_ACCOUNT_NAME}_connection"
)

EXPORT_COMMON_SYSAD_STORAGE_PRIMARY_KEY = (
    f"{COMMON_SYSAD_STORAGE_ACCOUNT_NAME}_primary_key"
)
EXPORT_COMMON_SYSAD_FILE_PRIMARY_KEY = f"{COMMON_SYSAD_FILE_ACCOUNT_NAME}_primary_key"
EXPORT_COMMON_SYSAD_FILE_CONNECTION_STRING = (
    f"{COMMON_SYSAD_FILE_ACCOUNT_NAME}_connection"
)

EXPORT_COMMON_SYSAD_COSMOSDB_PRIMARY_KEY = f"{COMMON_SYSAD_COSMOSDB_NAME}_primary_key"
EXPORT_COMMON_SYSAD_COSMOSDB_CONNECTION_STRING = (
    f"{COMMON_SYSAD_COSMOSDB_NAME}_connection"
)

# Bastion management resources
BM_AZURE_STORAGE_ACCOUNT_NAME = COMMON_SYSAD_STORAGE_ACCOUNT_NAME
BM_LOGIC_REGISTER_NAME = "logic-bm-register-dev"
BM_LOGIC_HANDLE_NAME = "logic-bm-handle-dev"  # NOT USED
BM_APPSERVICE_PLAN_NAME = "func-bm-handler-dev"
BM_FUNC_HANDLER_NAME = "func-bm-handler-dev"
BM_COSMOS_DB_NAME = "cosmos-bm-sysad-dev"
BM_COSMOS_CONTAINER_NAME = "BastionManagement"
BM_COSMOS_ITEM_NAME = "Entries"
BM_COSMOS_PRIMARY_PARTITION_KEY = "/title"
