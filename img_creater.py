import json
import time
import base64
import requests
import configparser

def get_api_keys(config_file):

    config = configparser.ConfigParser()
    config.read(config_file)
    print(config)

    result = {}
    for service in config.sections():
        result[service] = {
            'key': config[service]['api'],
            'secret_key': config[service]['secret_key'],
        }
    print(result)
    return result

class FusionBrainAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    def get_pipeline(self):
        response = requests.get(self.URL + 'key/api/v1/pipelines', headers=self.AUTH_HEADERS)
        data = response.json()
        return data[0]['id']

    def generate(self, prompt, pipeline, images=1, width=1024, height=1024):
        params = {
            "type": "GENERATE",
            "numImages": images,
            "width": width,
            "height": height,
            "generateParams": {
                "query": f'{prompt}'
            }
        }

        data = {
            'pipeline_id': (None, pipeline),
            'params': (None, json.dumps(params), 'application/json')
        }
        response = requests.post(self.URL + 'key/api/v1/pipeline/run', headers=self.AUTH_HEADERS, files=data)
        data = response.json()
        return data['uuid']

    def check_generation(self, request_id, attempts=10, delay=10):
        while attempts > 0:
            response = requests.get(self.URL + 'key/api/v1/pipeline/status/' + request_id, headers=self.AUTH_HEADERS)
            data = response.json()
            if data['status'] == 'DONE':
                return data['result']['files']

            attempts -= 1
            time.sleep(delay)


if __name__ == '__main__':
    api_keys = get_api_keys("img_api.ini")['Fusion Brain']
    api = FusionBrainAPI('https://api-key.fusionbrain.ai/', api_keys['key'], api_keys['secret_key'])
    pipeline_id = api.get_pipeline()
    uuid = api.generate("honey badger", pipeline_id)
    files = api.check_generation(uuid)
    image_base64 = files[0]
    image_data = base64.b64decode(image_base64)
    with open("image.jpg", "wb") as file:
        file.write(image_data)
