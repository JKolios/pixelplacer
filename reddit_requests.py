import time
import datetime

import requests
from requests.adapters import HTTPAdapter
import addict

session = requests.Session()
session.mount('https://www.reddit.com', HTTPAdapter(max_retries=5))
session.headers['Origin'] = "https://hot-potato.reddit.com"


def init_reddit_session(username, password, client_id, client_secret):

    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
    }
    while True:
        request = session.post('https://www.reddit.com/api/v1/access_token', data=data,
                               auth=(client_id, client_secret))
        if request.ok:
            data = request.json()
            print("Session request response: ", data)
            break
        else:
            print("ERROR: ", request, request.text)
            time.sleep(5)
    session.headers['Authorization'] = "bearer {}".format(data["access_token"])


def get_current_color(ax, ay):
    while True:
        r = session.get(
            "http://reddit.com/api/place/pixel.json?x={}&y={}".format(ax, ay), timeout=5)
        if r.ok:
            data = r.json()
            print("Get current color response: ", data)
            break
        else:
            print("ERROR: ", r, r.text)
        time.sleep(5)

    print("Current color #{} set by {}".format(
        data["color"] if "color" in data else 0,
        data["user_name"] if "user_name" in data else "<nobody>")
    )

    return data["color"] if "color" in data else 0


def set_color(ax, ay, new_color):
    r = session.post("https://gql-realtime-2.reddit.com/query",
                     json={
                         'operationName': 'setPixel',
                         'variables': {
                             'input': {
                                 'actionName': 'r/replace:set_pixel',
                                 'PixelMessageData': {
                                     'coordinate': {
                                         'x': ax,
                                         'y': ay,
                                     },
                                     'colorIndex': new_color,
                                     'canvasIndex': 0,
                                 },
                             },
                         },
                         'query': 'mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
                     })

    data = addict.Dict(r.json())
    print("Set color request response: ", data)
    if "errors" not in data:
        print("Placed color.")
        return {"success": True, "ts": time.time()}
    elif data.errors[0].message == 'Ratelimited':
        next_timestamp = int(data.errors[0].extensions.nextAvailablePixelTs / 1000) + 1
        print("Rate limited, next allowed ts:{}".format(next_timestamp))
        print("Ts in wall clock time UTC:{}".format(
            datetime.datetime.utcfromtimestamp(next_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
        return {"success": False, "ts": next_timestamp}
    else:
        next_timestamp = time.time()+ 30
        print("Unknown error, retrying at ts:{}".format(next_timestamp))
        print("Ts in wall clock time UTC:{}".format(
            datetime.datetime.utcfromtimestamp(next_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
        return {"success": False, "ts":  next_timestamp}
