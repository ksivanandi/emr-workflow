import requests

resp = requests.get('http://10.32.22.16:56733/noteevents/55500')
if resp.status_code != 200:
        raise ApiError('GET /noteevents/<size> {}'.format(resp.status_code))
notes=resp.json()['json_notes']
