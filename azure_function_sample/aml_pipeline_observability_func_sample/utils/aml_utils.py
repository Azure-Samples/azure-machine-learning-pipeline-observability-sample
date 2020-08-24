import os
from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication


def get_service_principal_authentication():
    svc_pr = ServicePrincipalAuthentication(
        tenant_id=os.environ.get('TENANT_ID'),
        service_principal_id=os.environ.get('APP_ID'),
        service_principal_password=os.environ.get('SERVICE_PRINCIPAL_PASSWORD')
    )
    return svc_pr


def get_workspace():
    ws = Workspace(
        subscription_id=os.environ.get('SUBSCRIPTION_ID'),
        resource_group=os.environ.get('AML_RESOURCE_GROUP'),
        workspace_name=os.environ.get('AML_WORKSPACE_NAME'),
        auth=get_service_principal_authentication()
    )

    return ws
