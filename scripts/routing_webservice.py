# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import json
import joblib
import requests
from azureml.core.model import Model
from azureml.contrib.services.aml_response import AMLResponse


def init(): 
    global service_dict
    
    models_root_path = os.getenv('AZUREML_MODEL_DIR') 
    models_files = [os.path.join(path, f) for path,dirs,files in os.walk(models_root_path) for f in files]
    print(models_files)
    if len(models_files) > 1:
        raise RuntimeError('Found more than one model')

    service_dict = joblib.load(models_files[0])


# Rawdata example:
# rawdata='''{
#     "store": "Store1005", "brand": "tropicana", 
#     "forecast_horizon": 5, "model_type": "lr", "date_freq": "W-THU",
#     "data": {
#         "dates": ["2020-04-23", "2020-04-30", "2020-05-07"],
#         "values": [11450, 12235, 14713]
#     }
# }'''

def run(rawdata):

    metadata = format_input_data(json.loads(rawdata))

    # Get model forecasting endpoint
    try:
        model_name = '{t}_{s}_{b}'.format(t=metadata['model_type'], s=metadata['store'], b=metadata['brand'])
        service_url = service_dict[model_name]
    except KeyError:
        return AMLResponse('Model not found for store {s} and brand {b} of type {t}'.format(
            s=metadata['store'], b=metadata['brand'], t=metadata['model_type']
        ), 400)

    # Call endpoint to get forecasting
    response, status = call_model_webservice(service_url, rawdata)
    
    return AMLResponse(response, status)


def call_model_webservice(url, rawdata): 
    ''' Call the model webservice to get the forecasting '''
    response = requests.post(url, data=rawdata, headers={'Content-Type': 'application/json'})
    return response.text, response.status_code


def format_input_data(input_data):
    ''' Format data received as input '''
    metadata = {k:v for k,v in input_data.items() if k != 'data'}
    return metadata
