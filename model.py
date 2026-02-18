import requests
import base64


def get_prediction(image_data):
    """Run image through AI model API. image_data should be base64 encoded bytes."""
    url = 'https://askai.aiclub.world/3fc9f175-9c15-43fd-b9fe-9751ec2f53b4'
    r = requests.post(url, data=image_data, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get('predicted_label', data.get('prediction', str(data)))
