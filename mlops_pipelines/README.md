# Instructions

## 1. Setup Pipeline

- Create a variable group called **``manymodels-vg``**, with the following variables:

| Variable Name               | Short description |
| --------------------------- | ----------------- |
| NAMESPACE                   | Unique naming prefix for created resources |
| LOCATION                    | [Azure location](https://azure.microsoft.com/en-us/global-infrastructure/locations/), no spaces |
| RESOURCE_GROUP              | Azure Resource Group name. Resource group should be already created |
| SERVICECONNECTION_GROUP     | Azure Resource Manager Service Connection name. See more [here](https://github.com/microsoft/MLOpsPython/blob/master/docs/getting_started.md#create-an-azure-devops-service-connection-for-the-azure-resource-manager) |
| SERVICECONNECTION_WORKSPACE (not used for now) | Azure ML Workspace Service Connection name. See more [here](https://github.com/microsoft/MLOpsPython/blob/master/docs/getting_started.md#create-an-azure-devops-service-connection-for-the-azure-ml-workspace) |

- Create Service Connection with the name set in SERVICECONNECTION_GROUP, setting the subscription and the resource group (which should be already created).

- Create the Pipeline as in [here](https://github.com/microsoft/MLOpsPython/blob/master/docs/getting_started.md#create-the-iac-pipeline), selecting branch **``feature/mlops``**setting the path to [/mlops_pipelines/1-setup/setup-pipeline.yml](1-setup/setup-pipeline.yml).
