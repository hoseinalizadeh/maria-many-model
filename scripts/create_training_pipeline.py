# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import pathlib
import argparse
from azureml.core import Workspace, Experiment, Dataset, Environment
from azureml.core.conda_dependencies import CondaDependencies
from azureml.core.compute import AmlCompute
from azureml.pipeline.core import Pipeline, PipelineData
from azureml.contrib.pipeline.steps import ParallelRunConfig, ParallelRunStep


def create_training_pipeline(ws, dataset_name, version):

    # Get input dataset
    dataset = Dataset.get_by_name(ws, name=dataset_name)
    dataset_input = dataset.as_named_input(dataset_name)

    # Set output
    datastore = ws.get_default_datastore()
    output_dir = PipelineData(name='training_output', datastore=datastore)

    # Set up ParallelRunStep
    parallel_run_config = get_parallel_run_config(ws, dataset_name)
    parallel_run_step = ParallelRunStep(
        name='many-models-training',
        parallel_run_config=parallel_run_config,
        inputs=[dataset_input],
        output=output_dir,
        allow_reuse=False,
        arguments=[
            '--target_column', 'Quantity', 
            '--n_test_periods', 6, 
            '--forecast_granularity', 7, 
            '--timestamp_column', 'WeekStarting', 
            '--model_type', 'lr'
        ]
    )

    # Create the pipeline
    train_pipeline = Pipeline(workspace=ws, steps=[parallel_run_step])
    train_pipeline.validate()

    published_pipeline = train_pipeline.publish(
        name='many-models-training',
        description="Many Models training/retraining pipeline",
        version=version,
        continue_on_step_failure = False
    )

    return published_pipeline.id


def get_parallel_run_config(ws, dataset_name, compute_name="cpu-compute", processes_per_node=8, node_count=3, timeout=180):

    # Configure environment for ParallelRunStep
    train_env = Environment(name="many_models_environment")
    train_conda_deps = CondaDependencies.create(pip_packages=['sklearn'])
    train_env.python.conda_dependencies = train_conda_deps

    # Get the compute target
    compute = AmlCompute(ws, compute_name)

    # Set run tags
    tags = {
        'dataset_name': dataset_name,
        'node_count': node_count,
        'process_count_per_node': processes_per_node,
        'timeout': timeout
    }

    # Set up ParallelRunStep configuration
    scripts_dir = pathlib.Path(__file__).parent.absolute().__str__()
    parallel_run_config = ParallelRunConfig(
        source_directory=scripts_dir,
        entry_script='train.py',
        mini_batch_size="1",
        run_invocation_timeout=timeout,
        error_threshold=10,
        output_action='append_row',
        environment=train_env,
        process_count_per_node=processes_per_node,
        compute_target=compute,
        node_count=node_count
    )

    return parallel_run_config


def parse_args(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--subscription-id', required=True, type=str)
    parser.add_argument('--resource-group', required=True, type=str)
    parser.add_argument('--workspace-name', required=True, type=str)
    parser.add_argument("--version", required=True, type=str)
    parser.add_argument("--dataset", type=str, default='oj_sales_data')
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

    pipeline_id = create_training_pipeline(ws, dataset_name=args.dataset, version=args.version)
    print(pipeline_id)
