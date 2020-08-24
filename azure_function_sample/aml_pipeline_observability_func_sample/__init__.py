import azure.functions as func
from aml_pipeline_observability_func_sample.event_processor import process_event


def main(event: func.EventGridEvent):
    process_event(event.get_json())
