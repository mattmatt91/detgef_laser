import requests

api_url = 'http://192.168.2.123:8022/laser'  

# data = {
#     "power": 0.2,
#     "duration": 10,
#     "pilot": True
# }


def send_msg(data:dict):
    requests.post('http://192.168.2.123:8022/laser', json=data)

    