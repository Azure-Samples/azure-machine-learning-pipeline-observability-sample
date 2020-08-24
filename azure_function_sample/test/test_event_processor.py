import os
import pytest
from aml_pipeline_observability_func_sample.event_processor import process_event, to_run_metrics
from mock import patch, call, Mock


def test_process_event_raises_value_error_without_run_id():
    # arrange
    event = {}

    # act/assert
    with pytest.raises(ValueError):
        process_event(event)


@patch.dict(os.environ, {'SUBSCRIPTION_ID': 'test_subscription_id', 'AML_RESOURCE_GROUP': 'test_aml_resource_group',
                         'AML_WORKSPACE_NAME': 'test_aml_workspace_name'})
def test_to_run_metrics():
    # arrange
    event = {
        'experimentName': 'test_experiment',
        'experimentId': 'test_experiment_id'
    }

    run_details = {
        'runId': 'test_run_id',
        'startTimeUtc': '2020-08-19T08:45:00.585171Z',
        'endTimeUtc': '2020-08-19T08:47:00.585171Z',
        'status': 'Completed',
        'target': 'test-compute',
        'properties': {
            'azureml.runsource': 'Step-Run',
            'StepType': 'PythonScript'
        }
    }

    expected_run_metrics = {
        'resourceGroup': 'test_aml_resource_group',
        'amlWorkSpace': 'test_aml_workspace_name',
        'subscriptions': 'test_subscription_id',
        'run_id': 'test_run_id',
        'start_time_utc': '2020-08-19T08:45:00.585171Z',
        'end_time_utc': '2020-08-19T08:47:00.585171Z',
        'experimentName': 'test_experiment',
        'experimentId': 'test_experiment_id',
        'status': 'Completed',
        'compute_target': 'test-compute',
        'run_type': 'Step-Run',
        'step_type': 'PythonScript'
    }

    # act
    actual_run_metrics = to_run_metrics(run_details, event)

    # assert

    assert actual_run_metrics == expected_run_metrics


@patch('aml_pipeline_observability_func_sample.event_processor.get_workspace')
@patch('aml_pipeline_observability_func_sample.event_processor.save_to_app_insight')
@patch('aml_pipeline_observability_func_sample.event_processor.Experiment')
@patch('aml_pipeline_observability_func_sample.event_processor.Run')
@patch.dict(os.environ, {'APPINSIGHTS_CONNECTION_STRING': 'test_connection'})
def test_save_to_app_insight_not_called_if_end_time_utc_is_missing_in_run_details(mock_run, mock_experiment,
                                                                                  mock_save_to_app_insight,
                                                                                  mock_get_workspace):
    # arrange
    event = {
        'runId': 'test_run_id',
        'experimentName': 'test',
        'experimentId': 'test_exp_id'
    }

    mock_get_workspace.return_value = 'test_workspace'
    mock_experiment.return_value = 'test_experiment'
    mock_run_obj = Mock()
    mock_run.return_value = mock_run_obj
    mock_run_obj.get_details.return_value = {}

    expected_experiment_call = call(workspace='test_workspace', name='test')
    expected_run_call = call('test_experiment', 'test_run_id')

    # act
    process_event(event)

    # assert
    assert mock_save_to_app_insight.call_count == 0
    assert expected_experiment_call in mock_experiment.mock_calls
    assert expected_run_call in mock_run.mock_calls


@patch('aml_pipeline_observability_func_sample.event_processor.to_run_metrics')
@patch('aml_pipeline_observability_func_sample.event_processor.get_workspace')
@patch('aml_pipeline_observability_func_sample.event_processor.save_to_app_insight')
@patch('aml_pipeline_observability_func_sample.event_processor.Experiment')
@patch('aml_pipeline_observability_func_sample.event_processor.Run')
@patch.dict(os.environ, {'APPINSIGHTS_CONNECTION_STRING': 'test_connection'})
def test_save_to_app_insight_called_if_end_time_utc_is_present_in_run_details(mock_run, mock_experiment,
                                                                              mock_save_to_app_insight,
                                                                              mock_get_workspace, mock_to_run_metrics):
    # arrange
    event = {
        'runId': 'test_run_id',
        'experimentName': 'test_experiment',
        'experimentId': 'test_experiment_id'
    }
    dummy_run_details = {
        'runId': 'test_run_id',
        'startTimeUtc': '2020-08-19T08:45:00.585171Z',
        'endTimeUtc': '2020-08-19T08:47:00.585171Z',
        'status': 'Completed',
        'target': 'test-compute',
        'properties': {
            'azureml.runsource': 'Step-Run',
            'StepType': 'PythonScript'
        }
    }

    dummy_run_metrics = {
        'resourceGroup': 'test_aml_resource_group',
        'amlWorkSpace': 'test_aml_workspace_name',
        'subscriptions': 'test_subscription_id',
        'run_id': 'test_run_id',
        'start_time_utc': '2020-08-19T08:45:00.585171Z',
        'end_time_utc': '2020-08-19T08:47:00.585171Z',
        'experimentName': 'test_experiment',
        'experimentId': 'test_experiment_id',
        'status': 'Completed',
        'compute_target': 'test-compute',
        'run_type': 'Step-Run',
        'step_type': 'PythonScript'
    }

    mock_get_workspace.return_value = 'test_workspace'
    mock_experiment.return_value = 'test_experiment'
    mock_to_run_metrics.return_value = dummy_run_metrics
    mock_run_obj = Mock()
    mock_run.return_value = mock_run_obj
    mock_run_obj.get_details.return_value = dummy_run_details

    expected_experiment_call = call(workspace='test_workspace', name='test_experiment')
    expected_run_call = call('test_experiment', 'test_run_id')
    expected_to_run_metrics_call = call(dummy_run_details, event)
    expected_save_to_app_insight_call = call(dummy_run_metrics, 'test_connection')

    # act
    process_event(event)

    # assert
    assert mock_save_to_app_insight.call_count == 1
    assert expected_save_to_app_insight_call in mock_save_to_app_insight.mock_calls
    assert expected_experiment_call in mock_experiment.mock_calls
    assert expected_run_call in mock_run.mock_calls
    assert expected_to_run_metrics_call in mock_to_run_metrics.mock_calls
