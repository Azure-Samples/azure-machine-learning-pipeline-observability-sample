import logging
from opencensus.ext.azure.log_exporter import AzureLogHandler

logger = logging.getLogger(__name__)
logger.setLevel("INFO")


def save_to_app_insight(metrics: dict, app_insight_connection: str):
    logger.addHandler(AzureLogHandler(
        connection_string=app_insight_connection,
        enable_standard_metrics=False)
    )
    properties = {'custom_dimensions': metrics}
    logger.info('aml_pipeline_run_metrics', extra=properties)
