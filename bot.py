from ast import Str
import time
import datetime
from tkinter.messagebox import NO
from typing import Dict

import requests
import requests.adapters
import addict

import utils
import closest_colors

class RedditRequestError(Exception):
    def __init__(self, status_code, response_text, message="Reddit Request Error"):
        self.message = message
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(self.message)

class RedditAuthError(RedditRequestError):
    def __init__(self, status_code, response_text, message="Reddit Authentication Error"):
        super().__init__(status_code, response_text, message)


class Bot(object):
    def __init__(self, username, password, app_id, app_secret, image, origin, bot_usernames) -> None:
        self.username = username
        self.password = password
        self.app_id = app_id
        self.app_secret = app_secret
        self.image = image
        self.origin = origin
        self.bot_usernames = bot_usernames

        self.session = requests.Session()
        self.session.mount('https://www.reddit.com',
                           requests.adapters.HTTPAdapter(max_retries=5))
        self.session.headers['Origin'] = "https://hot-potato.reddit.com"

    def start_loop(self) -> None:
        self._auth_loop()
        while True:
            try:
                self._loop_iteration()
            except RedditRequestError as e:
                print("Caught reddit request error")
                print("Code: {}, response:{}".format(e.status_code, e.response_text))
                print("Trying reauth")
                self._auth_loop()

    def _auth_loop(self) -> None:
        try:
            self._init_reddit_session()
        except RedditAuthError as e:
            print("Caught reddit request error")
            print("Code: {}, response:{}".format(e.status_code, e.response_text))
            print("Trying reauth")
            self._sleep_for(15, "auth request fallback")
            self._auth_loop()

    def _loop_iteration(self) -> None:
        print("starting image placement for img height: {}, width: {}".format(
            self.image.height, self.image.width))
        arr2d = utils.shuffle2d([[[i, j] for i in range(self.image.width)]
                                 for j in range(self.image.height)])

        for y in range(self.image.width):
            for x in range(self.image.height):
                xx = arr2d[x][y]
                pixel = self.image.getpixel((xx[0], xx[1]))

                if pixel[3] == 0:
                    print("Transparent pixel, ignoring.")
                    continue
                
                new_color = closest_colors.find_palette(
                    (pixel[0], pixel[1], pixel[2]))

                ax = xx[0] + int(self.origin[0])
                ay = xx[1] + int(self.origin[1])

                message = "Getting user who last modified pixel {},{}".format(
                    ax, ay)
                print(message)
                last_modified_user = self._get_last_modified_user(
                    ax, ay)
                if last_modified_user in self.bot_usernames:
                    self._sleep_for(.25, "Color already set by one of our bots")
                    continue

                set_color_result = self._set_color(ax, ay, new_color)
                sleep_for = set_color_result["ts"] - time.time() + 1
                self._sleep_for(sleep_for, "In cooldown")

        self._sleep_for(60, "all pixels placed")

    def _init_reddit_session(self) -> None:
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password':  self.password,
        }

        request = self.session.post('https://www.reddit.com/api/v1/access_token', data=data,
                                    auth=(self.app_id,  self.app_secret))
        if request.ok:
            data = request.json()
            print("Session request response: ", data)
            self.session.headers['Authorization'] = "bearer {}".format(
                data["access_token"])
        else:
           raise RedditAuthError(request.status_code, request.text)

    def _get_last_modified_user(self, ax, ay) -> Str:
        canvIndex = 0
        if ax >= 1000:
            ax = ax % 1000
            canvIndex = 1

        r = self.session.post("https://gql-realtime-2.reddit.com/query",
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
                                              'canvasIndex': canvIndex,
                                          },
                                      },
                                  },
                                  'query': 'mutation pixelHistory($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetTileHistoryResponseMessageData {\n            lastModifiedTimestamp\n            userInfo {\n              userID\n              username\n              __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
                              })

        if not r.ok:
            raise RedditRequestError(r.status_code, r.text)

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

    def _set_color(self, ax, ay, new_color) -> Dict:
        canvIndex = 0
        if ax >= 1000:
            ax = ax % 1000
            canvIndex = 1

        r = self.session.post("https://gql-realtime-2.reddit.com/query",
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
                                              'canvasIndex': canvIndex,
                                          },
                                      },
                                  },
                                  'query': 'mutation setPixel($input: ActInput!) {\n  act(input: $input) {\n    data {\n      ... on BasicMessage {\n        id\n        data {\n          ... on GetUserCooldownResponseMessageData {\n            nextAvailablePixelTimestamp\n            __typename\n          }\n          ... on SetPixelResponseMessageData {\n            timestamp\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n',
                              })

        if not r.ok:
            raise RedditRequestError(r.status_code, r.text)

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

    def _sleep_for(self, duration, reason="Unknown"):
        print("Bot {} will sleep for {} seconds. Reason:{}".format(
            self.username, duration, reason))
        try:
            time.sleep(duration)
        except ValueError:
            print("Invalid sleep duration, continuing")
