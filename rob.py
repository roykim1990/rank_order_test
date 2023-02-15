from modelop.monitors.assertions import check_input_types
from pathlib import Path
import modelop.schema.infer as infer
import pandas as pd
import logging
import json

logger = logging.getLogger(__name__)

BINS = []
BUCKET_COL = ''
POSITIVE_LABEL = 1
LABEL_COLUMN = None

# modelop.init
def init(init_param):
    global BINS
    global BUCKET_COL
    global POSITIVE_LABEL
    global LABEL_COLUMN

    job_json = init_param

    BINS = [300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800]
    BUCKET_COL= "ally_score"
    POSITIVE_LABEL = 1

    if job_json is not None:
        logger.info(
            "Parameter 'job_json' is present and will be used to extract "
            "'label_column' and 'score_column'."
        )
        input_schema_definition = infer.extract_input_schema(job_json)
        monitoring_parameters = infer.set_monitoring_parameters(
            schema_json=input_schema_definition, check_schema=True
        )
        LABEL_COLUMN = monitoring_parameters['label_column']
    else:
        logger.info(
            "Parameter 'job_json' it not present, attempting to use "
            "'label_column' and 'score_column' instead."
        )
        if LABEL_COLUMN is None:
            missing_args_error = (
                "Parameter 'job_json' is not present,"
                " but 'label_column'. "
                "'label_column' input parameter is"
                " required if 'job_json' is not provided."
            )
            logger.error(missing_args_error)
            raise Exception(missing_args_error)
    check_input_types(
        inputs=[
            {"label_column": LABEL_COLUMN}
        ],
        types=(str),
    )

# modelop.metrics
def metrics(data: pd.DataFrame) -> dict:
    bucketed_data = data.groupby([LABEL_COLUMN, pd.cut(data[BUCKET_COL], BINS)]).size().unstack().T
    bucketed_data['percent'] =  (bucketed_data[POSITIVE_LABEL] / data.shape[0])
    list_of_values = []
    for i, row in bucketed_data.iterrows():
        values = {}
        values[f'{BUCKET_COL}_bucket'] = str(i)
        values['percent'] = row['percent']
        list_of_values.append({'values': values})
    return {'Rank_Order': list_of_values}

def main():
    raw_json = Path('./example_job.json').read_text()
    init_param = {'rawJson': raw_json}
    init(init_param)
    print('initialized parameters from job_json.')
    print(BINS)
    print(BUCKET_COL)
    print(LABEL_COLUMN)
    print(POSITIVE_LABEL)
    data = pd.read_csv('./rob_test.csv')
    print('read data.')
    result = metrics(data)
    print(json.dumps(result, indent=3, sort_keys=True))
    print('done.')
    
if __name__ == '__main__':
	main()