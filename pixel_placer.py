import sys
import csv
import concurrent.futures

from PIL import Image

import bot


def main():
    account_file_path = sys.argv[1]
    img_path = sys.argv[2]
    origin_x = sys.argv[3]
    origin_y = sys.argv[4]

    img = Image.open(img_path)

    accounts = []
    with open(account_file_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            accounts.append({
                'username': row[0],
                'password': row[1],
                'app_id': row[2],
                'app_secret': row[3],
            })
            line_count += 1
    print(f'Processed {line_count} accounts.')

    bot_usernames = [account['username'] for account in accounts]
    print("Bot username list: {}".format(bot_usernames))

    bots = [
        bot.Bot(
            account['username'],
            account['password'],
            account['app_id'],
            account['app_secret'],
            img,
            (origin_x, origin_y),
            bot_usernames
        ) for account in accounts]

    with concurrent.futures.ProcessPoolExecutor(max_workers=len(bots)) as executor:
        bot_futures = {executor.submit(bot.start_loop): bot.username for bot in bots}
        for future in concurrent.futures.as_completed(bot_futures):
            print('Bot {} finished, result:'.format(bot_futures[future], future.result()))


if __name__ == "__main__":
    main()
