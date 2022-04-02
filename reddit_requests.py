import time
import datetime

import requests
from requests.adapters import HTTPAdapter
import addict

session = requests.Session()
session.mount('https://www.reddit.com', HTTPAdapter(max_retries=5))
session.headers['Origin'] = "https://hot-potato.reddit.com"


class RedditRequestError(Exception):
    pass


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
            time.sleep(10)
    session.headers['Authorization'] = "bearer {}".format(data["access_token"])


def get_last_modified_user(ax, ay):
    r = session.post("https://gql-realtime-2.reddit.com/query",
                     json={
                         'operationName': 'pixelHistory',
                         'variables': {
                             'input': {
                                 'actionName': 'r/replace:get_tile_history',
                                 'PixelMessageData': {
                                     'coordinate': {
                                         'x': ax,
                                         'y': ay,
                                     },
                                     'colorIndex': 0,
                                     'canvasIndex': 0,
                                 },
                             },
                         },
                         'query': 'mutation pixelHistory($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetTileHistoryResponseMessageData {\n            lastModifiedTimestamp\n            userInfo {\n              userID\n              username\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
                     })

    if not r.ok:
        # Assuming for now that all non-200 status codes are caused by
        # token expirations
        raise RedditRequestError

    data = addict.Dict(r.json())
    print("Get last modified user request response: ", data)
    last_modified_user = data.data.act.data[0].data.userInfo.username
    last_modified_ts = int(
        data.data.act.data[0].data.lastModifiedTimestamp / 1000)
    print(last_modified_ts)
    last_modified_utc = datetime.datetime.utcfromtimestamp(
        last_modified_ts).strftime('%Y-%m-%d %H:%M:%S')
    print("Pixel {},{} Last modified by {} at UTC: {}".format(
          ax, ay, last_modified_user, last_modified_utc))
    return last_modified_user


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

    if not r.ok:
        # Assuming for now that all non-200 status codes are caused by
        # token expirations
        raise RedditRequestError

    data = addict.Dict(r.json())
    print("Set color request response: ", data)
    if "errors" not in data:
        print("Placed color.")
        next_timestamp = int(
            data.data.act.data[0].data.nextAvailablePixelTimestamp / 1000) + 1
        print("Next attempt at ts:{}".format(next_timestamp))
        print("Ts in wall clock time UTC:{}".format(
            datetime.datetime.utcfromtimestamp(next_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
        return {"success": True, "ts": next_timestamp}
    elif data.errors[0].message == 'Ratelimited':
        next_timestamp = int(
            data.errors[0].extensions.nextAvailablePixelTs / 1000) + 1
        print("Rate limited, next allowed ts:{}".format(next_timestamp))
        print("Ts in wall clock time UTC:{}".format(
            datetime.datetime.utcfromtimestamp(next_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
        return {"success": False, "ts": next_timestamp}
    else:
        next_timestamp = time.time() + 30
        print("Unknown error, retrying at ts:{}".format(next_timestamp))
        print("Ts in wall clock time UTC:{}".format(
            datetime.datetime.utcfromtimestamp(next_timestamp).strftime('%Y-%m-%d %H:%M:%S')))
        return {"success": False, "ts":  next_timestamp}
