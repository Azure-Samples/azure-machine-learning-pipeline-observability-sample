import logging
import os
from azureml.core import Experiment, Run
from aml_pipeline_observability_func_sample.utils.aml_utils import get_workspace
from aml_pipeline_observability_func_sample.utils.app_insight_utils import save_to_app_insight

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def process_event(event):
    if 'runId' not in event:
        raise ValueError('Malformed Event. Run Id does not exits. Event: %s', event)

    logger.info(f'Event Details: {event}')

    exp = Experiment(workspace=get_workspace(), name=event['experimentName'])
    run = Run(exp, event['runId'])
    run_details = run.get_details()
    app_insight_connection = os.environ.get('APPINSIGHTS_CONNECTION_STRING')

    if 'endTimeUtc' in run_details:
        logger.info(f'Run details: {run_details}')

        """
        Just for sample here we are saving metrics to Application Insight after collecting details from 'run_details'
        & 'event'. You can store it to any other storage/database as well.
        """
        save_to_app_insight(to_run_metrics(run_details, event), app_insight_connection)
    else:
        logging.info('Ignoring event. As step/pipeline is still running. Event: %s', event)


def to_run_metrics(run_details: dict, event: dict) -> dict:
    """
    This is just a sample of few important metrics which we can collect.
    For more values please take look on 'run_details' & 'event' dictionaries.
    """

    metrics_dict = {
        'resourceGroup': os.environ.get('AML_RESOURCE_GROUP'),
        'amlWorkSpace': os.environ.get('AML_WORKSPACE_NAME'),
        'subscriptions': os.environ.get('SUBSCRIPTION_ID'),
        'run_id': run_details['runId'],
        'start_time_utc': run_details['startTimeUtc'],
        'end_time_utc': run_details['endTimeUtc'],
        'experimentName': event['experimentName'],
        'experimentId': event['experimentId'],
        'status': run_details['status']
    }

    if 'target' in run_details:
        metrics_dict['compute_target'] = run_details['target']

    if 'properties' in run_details:
        if 'azureml.runsource' in run_details['properties']:
            metrics_dict['run_type'] = run_details['properties']['azureml.runsource']
        if 'StepType' in run_details['properties']:
            metrics_dict['step_type'] = run_details['properties']['StepType']

    return metrics_dict
