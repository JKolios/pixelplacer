import sys
import time

from PIL import Image

import closest_colors
import reddit_requests
import utils


def place_pixel(ax, ay, new_color):
    print("Placing color #{} at {} {}".format(new_color, ax, ay))
    place_pixel_result = reddit_requests.set_color(ax, ay, new_color)
    sleep_for = place_pixel_result["ts"] - time.time() + 1
    print("Will sleep for {} seconds".format(sleep_for))
    try:
        time.sleep(sleep_for)
    except ValueError:
        print("Next timestamp was in the past, continuing")


def main():
    _, img_path, origin_x, origin_y, username, password, client_id, client_secret, other_bot_usernames = sys.argv
    img = Image.open(img_path)
    bot_usernames = [username]
    bot_usernames.extend(other_bot_usernames.split(','))
    print("Bot username list: {}".format(bot_usernames))

    reddit_requests.init_reddit_session(
        username, password, client_id, client_secret)
    while True:
        print("starting image placement for img height: {}, width: {}".format(
            img.height, img.width))
        arr2d = utils.shuffle2d([[[i, j] for i in range(img.width)]
                                 for j in range(img.height)])
        total = img.width * img.height
        checked = 0
        for y in range(img.width):
            for x in range(img.height):
                xx = arr2d[x][y]
                pixel = img.getpixel((xx[0], xx[1]))

                if pixel[3] > 0:
                    new_color = closest_colors.find_palette(
                        (pixel[0], pixel[1], pixel[2]))

                    ax = xx[0] + int(origin_x)
                    ay = xx[1] + int(origin_y)

                    try:
                        message = "Getting user who last modified pixel {},{}".format(
                            ax, ay)
                        print(message)
                        last_modified_user = reddit_requests.get_last_modified_user(
                            ax, ay)
                        if last_modified_user in bot_usernames:
                            print("Color already set by one of our bots")
                            time.sleep(.25)
                            continue
                        place_pixel(ax, ay, new_color)
                    except reddit_requests.RedditRequestError:
                        print("Caught reddit request error, reauthenticating")
                        reddit_requests.init_reddit_session(
                            username, password, client_id, client_secret)
                    checked += 1
        message = "All pixels placed, sleeping {}s..."
        waitTime = 60
        while(waitTime > 0):
            m = message.format(waitTime)
            time.sleep(1)
            waitTime -= 1
            if waitTime > 0:
                print(m, end="              \r")
            else:
                print(m)


if __name__ == "__main__":
    main()
