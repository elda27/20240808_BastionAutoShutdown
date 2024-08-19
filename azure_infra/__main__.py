"""A Python Pulumi program"""

# import debugpy

# debugpy.listen(("localhost", 5678))
# debugpy.wait_for_client()

import pulumi
from azure_infra.main import main

main()
