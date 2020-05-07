# Instructions

## Before creating the pipelines

- Create a variable group called **``manymodels-vg``**, with the following variables:

| Variable Name               | Short description |
| --------------------------- | ----------------- |
| NAMESPACE                   | Unique naming prefix for created resources |
| LOCATION                    | [Azure location](https://azure.microsoft.com/en-us/global-infrastructure/locations/), no spaces |
| RESOURCE_GROUP              | Azure Resource Group name. Resource group should be already created |
| SERVICECONNECTION_GROUP     | Azure Resource Manager Service Connection name. See more [here](https://github.com/microsoft/MLOpsPython/blob/master/docs/getting_started.md#create-an-azure-devops-service-connection-for-the-azure-resource-manager) |
| SERVICECONNECTION_WORKSPACE | Azure ML Workspace Service Connection name. See more [here](https://github.com/microsoft/MLOpsPython/blob/master/docs/getting_started.md#create-an-azure-devops-service-connection-for-the-azure-ml-workspace) |

- Create Service Connection with the name set in SERVICECONNECTION_GROUP, setting the subscription and the resource group (which should be already created).

## 1. Setup Pipeline

- Create the Pipeline as in [here](https://github.com/microsoft/MLOpsPython/blob/master/docs/getting_started.md#create-the-iac-pipeline), selecting branch **``feature/mlops``** and setting the path to [/mlops_pipelines/1-setup/setup-pipeline.yml](1-setup/setup-pipeline.yml).

## 2. Training Code Build Pipeline

- When the AML Workspace is already created (this is done in the 1st pipeline), create an AML Workspace service connection with the name set in SERVICECONNECTION_WORKSPACE.

- Create the pipeline selecting branch **``feature/mlops``** and setting the path to [/mlops_pipelines/2-training-code-build/training-code-build-pipeline.yml](2-training-code-build/training-code-build-pipeline.yml).

## 3. Modeling Pipeline (in progress - training for now)

- Create the pipeline selecting branch **``feature/mlops``** and setting the path to [/mlops_pipelines/3-modeling/modeling-pipeline.yml](3-modeling/modeling-pipeline.yml).
