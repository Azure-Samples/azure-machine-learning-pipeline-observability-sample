import os
from mock import patch, call
from aml_pipeline_observability_func_sample.utils.aml_utils import get_service_principal_authentication, get_workspace


@patch('aml_pipeline_observability_func_sample.utils.aml_utils.ServicePrincipalAuthentication')
@patch.dict(os.environ,
            {'TENANT_ID': 'test_tenant_id', 'APP_ID': 'test_app_id', 'SERVICE_PRINCIPAL_PASSWORD': 'test_pass'})
def test_get_service_principal_authentication(mock_service_principal_authentication):
    # arrange
    expected_svp_call = call(tenant_id='test_tenant_id', service_principal_id='test_app_id',
                             service_principal_password='test_pass')

    # act
    get_service_principal_authentication()

    # assert
    assert expected_svp_call in mock_service_principal_authentication.mock_calls


@patch('aml_pipeline_observability_func_sample.utils.aml_utils.Workspace')
@patch('aml_pipeline_observability_func_sample.utils.aml_utils.get_service_principal_authentication')
@patch.dict(os.environ, {'SUBSCRIPTION_ID': 'test_subscription_id', 'AML_RESOURCE_GROUP': 'test_aml_resource_group',
                         'AML_WORKSPACE_NAME': 'test_aml_workspace_name'})
def test_get_workspace(mock_service_principal_auth, mock_workspace):
    # arrange
    expected_workspace_call = call(subscription_id='test_subscription_id', resource_group='test_aml_resource_group',
                                   workspace_name='test_aml_workspace_name', auth=None)
    mock_service_principal_auth.return_value = None

    # act
    get_workspace()

    # assert
    assert expected_workspace_call in mock_workspace.mock_calls
