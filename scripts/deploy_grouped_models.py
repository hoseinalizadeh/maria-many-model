# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import pathlib
import argparse
import joblib
from azureml.core import Workspace, Model, Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.model import InferenceConfig
from azureml.core.webservice import AciWebservice


def deploy_model_groups(ws, nmodels, grouping_tags=None, exclude=[]):

    grouped_models = get_grouped_models(nmodels, grouping_tags, exclude=exclude)
    
    deployment_config = get_deployment_config()

    # Deploy groups
    endpoints = {}
    for group_name, group_models in grouped_models.items():
        service = deploy_model_group(ws, group_name, group_models, deployment_config)
        
        # Store pairs model - endpoint where the model is deployed
        for m in group_models:
            endpoints[m.name] = service.scoring_uri

    return endpoints


def get_grouped_models(nmodels, grouping_tags=None, exclude=[]):
    
    # Get all models registered in the workspace
    # all_models = Model.list(ws, latest=True)
    
    #FIXME parallel deployment
    all_stores = ['Store{}'.format(i) for i in range(138, 4129)]
    all_brands = ['dominicks', 'minute.maid', 'tropicana']
    all_models = [f'lr_{store}_{brand}' for store in all_stores for brand in all_brands]
    
    print(nmodels)
    models_todeploy = sorted(all_models)[:nmodels]
    models_todeploy = [Model(ws, name) for name in models_todeploy]

    # Group models by tags
    grouped_models = {}
    for m in models_todeploy:
        # Exclude models that follow conditions (routing meta-model)
        if any(m.tags[t] == v for t,v in exclude):
            continue
        
        group_name = '/'.join([m.tags[t] for t in grouping_tags]) if grouping_tags is not None else m.name
        group = grouped_models.setdefault(group_name, [])
        group.append(m)
    
    return grouped_models


def get_deployment_config():
    
    # Define inference environment
    forecast_env = Environment(name="many_models_environment")
    forecast_conda_deps = CondaDependencies.create(pip_packages=['azureml-defaults', 'sklearn'])
    forecast_env.python.conda_dependencies = forecast_conda_deps
    
    # Define inference configuration
    scripts_dir = pathlib.Path(__file__).parent.absolute().__str__()
    inference_config = InferenceConfig(
        entry_script='forecast_webservice.py',
        source_directory=scripts_dir,
        environment=forecast_env
    )

    # Define deploy configuration
    aci_config = AciWebservice.deploy_configuration(cpu_cores=1, memory_gb=1) #TODO generalize
    
    deployment_config = {
        'inference_config': inference_config,
        'deployment_config': aci_config,
    }
    
    return deployment_config


def deploy_model_group(ws, group_name, group_models, deployment_config):
    
    service_name = 'manymodels-{}'.format(group_name).lower()
    service = Model.deploy(
        workspace=ws,
        name=service_name,
        models=group_models,
        **deployment_config,
        overwrite=True
    )
    
    print('Deploying {}...'.format(service_name))
    service.wait_for_deployment(show_output=True)
    assert service.state == 'Healthy'
    
    return service


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--subscription-id', required=True, type=str)
    parser.add_argument('--resource-group', required=True, type=str)
    parser.add_argument('--workspace-name', required=True, type=str)
    parser.add_argument('--nmodels', required=True, type=int)
    parser.add_argument("--grouping-tags", type=lambda str: [t for t in str.split(',') if t])
    parser.add_argument("--routing-model-tag-name", type=str, default='ModelType')
    parser.add_argument("--routing-model-tag-value", type=str, default='_meta_')
    parser.add_argument("--endpoints-path", type=str, default='endpoints.pkl')
    args_parsed = parser.parse_args(args)
    return args_parsed


if __name__ == "__main__":
    args = parse_args()

    # Connect to workspace
    ws = Workspace.get(
        name=args.workspace_name,
        subscription_id=args.subscription_id,
        resource_group=args.resource_group
    )

    routing_model_tags = [(args.routing_model_tag_name, args.routing_model_tag_value)]

    endpoints = deploy_model_groups(ws, nmodels=args.nmodels, grouping_tags=args.grouping_tags, exclude=routing_model_tags)
    joblib.dump(endpoints, args.endpoints_path)
